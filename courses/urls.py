from django.urls import path
from .views import (
    CourseListView, CourseDetailView,
    CourseCreateView, CourseUpdateView,
    CourseEnrollView, SectionCreateView, VideoCreateView, EnrolledCoursesView, TeachingCoursesView,
    MarkVideoWatchedView, SubmitQuizView, CreateQuizView, CreateQuestionView, CreateChoiceView, GetUserQuizScoreView,
    DiscussionListCreateView, CommentCreateView, VoteDiscussionView, VoteCommentView, DiscussionUpdateDeleteView,
    CommentUpdateDeleteView
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:id>/', CourseDetailView.as_view(), name='course_detail'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/update/', CourseUpdateView.as_view(), name='course_update'),
    path('<int:course_id>/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
    path('<int:course_id>/sections/create/', SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:section_id>/videos/create/', VideoCreateView.as_view(), name='video_create'),
    path('my/enrolled/', EnrolledCoursesView.as_view(), name='enrolled_courses'),
    path('my/teaching/', TeachingCoursesView.as_view(), name='teaching_courses'),
    path('videos/<int:video_id>/watched/', MarkVideoWatchedView.as_view(), name='mark_video_watched'),
    path('quizzes/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='submit_quiz'),
    path('sections/<int:section_id>/quiz/create/', CreateQuizView.as_view(), name='create_quiz'),
    path('quizzes/<int:quiz_id>/questions/create/', CreateQuestionView.as_view(), name='create_question'),
    path('questions/<int:question_id>/choices/create/', CreateChoiceView.as_view(), name='create_choice'),
    path('quizzes/<int:quiz_id>/my-score/', GetUserQuizScoreView.as_view(), name='get_user_score'),
    path('courses/<int:course_id>/discussions/', DiscussionListCreateView.as_view(), name='discussion_list_create'),
    path('discussions/<int:discussion_id>/comments/create/', CommentCreateView.as_view(), name='comment_create'),
    path('discussions/<int:discussion_id>/vote/', VoteDiscussionView.as_view(), name='vote_discussion'),
    path('comments/<int:comment_id>/vote/', VoteCommentView.as_view(), name='vote_comment'),
    path('discussions/<int:pk>/', DiscussionUpdateDeleteView.as_view(), name='discussion_edit_delete'),
    path('comments/<int:pk>/', CommentUpdateDeleteView.as_view(), name='comment_edit_delete'),
]

