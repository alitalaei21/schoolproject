from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Section, Video, Quiz, Choice, QuizResult, Question, Discussion, Vote, Comment
from courses.serializers import CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer, \
    SectionSerializer, VideoSerializer, ChoiceSerializer, QuestionSerializer, QuizSerializer, DiscussionSerializer, \
    CommentSerializer


# Create your views here.
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class CourseUpdateView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        course = self.get_object()
        if course.teacher != self.request.user:
            raise PermissionDenied("شما مجاز به ویرایش این دوره نیستید.")
        serializer.save()





class CourseEnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound("دوره پیدا نشد.")

        if course.is_vip_only and not request.user.is_vip:
            return Response({"detail": "برای دسترسی به این دوره باید VIP باشید."}, status=403)

        course.students.add(request.user)
        return Response({"detail": "شما با موفقیت در این دوره ثبت‌نام شدید."})


class SectionCreateView(generics.CreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise NotFound("دوره یافت نشد.")

        if course.teacher != self.request.user:
            raise PermissionDenied("شما مدرس این دوره نیستید.")

        serializer.save(course=course)


class VideoCreateView(generics.CreateAPIView):
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        section_id = self.kwargs['section_id']
        try:
            section = Section.objects.select_related('course').get(id=section_id)
        except Section.DoesNotExist:
            raise NotFound("فصل پیدا نشد.")

        if section.course.teacher != self.request.user:
            raise PermissionDenied("شما مدرس این فصل نیستید.")

        serializer.save(section=section)

class EnrolledCoursesView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.enrolled_courses.all()

class TeachingCoursesView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.courses.all()


# courses/views.py (ادامه)

from .models import VideoProgress


class MarkVideoWatchedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            raise NotFound("ویدیو پیدا نشد.")

        progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'watched': True}
        )
        if not created and not progress.watched:
            progress.watched = True
            progress.save()

        return Response({"detail": "ویدیو به عنوان دیده‌شده علامت خورد."})






class SubmitQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.prefetch_related('questions__choices').get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise NotFound("آزمون پیدا نشد.")

        answers = request.data.get("answers")  # format: {question_id: choice_id}

        if not isinstance(answers, dict):
            raise ValidationError("فرمت پاسخ‌ها نادرست است.")

        correct = 0
        total = quiz.questions.count()

        for question in quiz.questions.all():
            selected_choice_id = answers.get(str(question.id))
            if not selected_choice_id:
                continue
            try:
                choice = Choice.objects.get(id=selected_choice_id, question=question)
                if choice.is_correct:
                    correct += 1
            except Choice.DoesNotExist:
                continue

        score = (correct / total) * 100 if total else 0

        QuizResult.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={"score": score}
        )

        return Response({
            "score": score,
            "correct_answers": correct,
            "total_questions": total
        })


class CreateQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        section_id = self.kwargs.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        if section.course.teacher != self.request.user:
            raise PermissionDenied("فقط مدرس دوره می‌تواند آزمون اضافه کند.")
        serializer.save(section=section)


class CreateQuestionView(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        if quiz.section.course.teacher != self.request.user:
            raise PermissionDenied("فقط مدرس می‌تواند سؤال اضافه کند.")
        serializer.save(quiz=quiz)
class CreateChoiceView(generics.CreateAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        if question.quiz.section.course.teacher != self.request.user:
            raise PermissionDenied("فقط مدرس می‌تواند گزینه اضافه کند.")
        serializer.save(question=question)


class GetUserQuizScoreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            result = QuizResult.objects.get(user=request.user, quiz_id=quiz_id)
        except QuizResult.DoesNotExist:
            raise NotFound("شما هنوز در این آزمون شرکت نکرده‌اید.")
        return Response({
            "score": result.score,
            "taken_at": result.taken_at
        })




class DiscussionListCreateView(generics.ListCreateAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Discussion.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        serializer.save(user=self.request.user, course=course)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        discussion_id = self.kwargs.get('discussion_id')
        discussion = get_object_or_404(Discussion, id=discussion_id)
        serializer.save(user=self.request.user, discussion=discussion)




class VoteDiscussionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, discussion_id):
        discussion = get_object_or_404(Discussion, id=discussion_id)
        value = request.data.get('value')

        if value not in [1, -1]:
            raise ValidationError({"detail": "value باید 1 (like) یا -1 (dislike) باشد."})

        vote = Vote.objects.filter(
            user=request.user,
            discussion=discussion,
            comment=None
        ).first()

        if vote:
            if vote.value == value:
                vote.delete()
                return Response({"detail": "رأی حذف شد."})
            else:
                vote.value = value
                vote.save()
                return Response({"detail": "رأی تغییر کرد."})
        else:
            Vote.objects.create(
                user=request.user,
                discussion=discussion,
                value=value
            )
            return Response({"detail": "رأی ثبت شد."})


class VoteCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        value = request.data.get('value')

        if value not in [1, -1]:
            raise ValidationError({"detail": "value باید 1 (like) یا -1 (dislike) باشد."})

        vote = Vote.objects.filter(
            user=request.user,
            comment=comment,
            discussion=None
        ).first()

        if vote:
            if vote.value == value:
                vote.delete()
                return Response({"detail": "رأی حذف شد."})
            else:
                vote.value = value
                vote.save()
                return Response({"detail": "رأی تغییر کرد."})
        else:
            Vote.objects.create(
                user=request.user,
                comment=comment,
                value=value
            )
            return Response({"detail": "رأی ثبت شد."})


class DiscussionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user and not self.request.user.is_staff:
            raise PermissionDenied("شما اجازه ویرایش این بحث را ندارید.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user and not self.request.user.is_staff:
            raise PermissionDenied("شما اجازه حذف این بحث را ندارید.")
        instance.delete()

class CommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.user and not self.request.user.is_staff:
            raise PermissionDenied("شما اجازه ویرایش این نظر را ندارید.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user and not self.request.user.is_staff:
            raise PermissionDenied("شما اجازه حذف این نظر را ندارید.")
        instance.delete()