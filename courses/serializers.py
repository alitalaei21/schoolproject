from courses.models import Video, Section, Course, VideoProgress, Choice, Question, Quiz, Comment, Discussion, Vote, \
    DiscussionSubscription
from user import serializers
from user.models import UserPublicSerializer
from user.serializers import UserSerializer


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_url', 'duration_seconds', 'order']
        read_only_fields = ['id']

class SectionSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'videos']
        read_only_fields = ['id']

class CourseListSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    student_count = serializers.IntegerField(source='student_count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'teacher', 'is_vip_only', 'student_count']


class CourseDetailSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    student_count = serializers.IntegerField(source='student_count', read_only=True)
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher',
            'is_vip_only', 'student_count', 'sections'
        ]
class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_vip_only']
# courses/serializers.py (ادامه)

class VideoProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProgress
        fields = ['video', 'watched', 'watched_at']
        read_only_fields = ['watched_at']

class CourseDetailSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    student_count = serializers.IntegerField(source='student_count', read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'teacher',
            'is_vip_only', 'student_count', 'sections', 'progress_percent'
        ]

    def get_progress_percent(self, course):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        all_videos = Video.objects.filter(section__course=course).count()
        watched_videos = VideoProgress.objects.filter(
            user=user,
            video__section__course=course,
            watched=True
        ).count()
        if all_videos == 0:
            return 0
        return round((watched_videos / all_videos) * 100)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'questions']



class CommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.votes.filter(value=1).count()

    def get_dislikes(self, obj):
        return obj.votes.filter(value=-1).count()


class DiscussionSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Discussion
        fields = ['id', 'course', 'user', 'title', 'content', 'created_at', 'comments']
        read_only_fields = ['user', 'created_at']

    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.votes.filter(value=1).count()

    def get_dislikes(self, obj):
        return obj.votes.filter(value=-1).count()



class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'value']



class DiscussionSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionSubscription
        fields = ['id', 'user', 'discussion', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        discussion = validated_data['discussion']
        return DiscussionSubscription.objects.update_or_create(user=user, discussion=discussion)[0]