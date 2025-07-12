from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings

class Course(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_vip_only = models.BooleanField(default=False)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def student_count(self):
        return self.students.count()

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    duration_seconds = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.title} - {self.title}"


class VideoProgress(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="video_progress")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="progresses")
    watched = models.BooleanField(default=True)
    watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')


class Quiz(models.Model):
    section = models.OneToOneField(Section, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"Quiz: {self.title}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=1024)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✖'})"

class QuizResult(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'quiz']




class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="discussions")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="discussions")
    title = models.CharField(max_length=255)
    attachment = models.FileField(
        upload_to='attachments/discussions/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'pdf', 'docx', 'zip'])]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="comments")
    attachment = models.FileField(
        upload_to='attachments/comments/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'pdf', 'docx', 'zip'])]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class Vote(models.Model):
    VOTE_CHOICES = (
        (1, 'like'),
        (-1, 'dislike'),
    )

    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True, blank=True, related_name="votes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="votes")

    class Meta:
        unique_together = ('user', 'discussion', 'comment')
