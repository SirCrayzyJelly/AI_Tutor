from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class QAEntry(models.Model):
    lecture_id = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="qa_entries")
    question = models.TextField()
    answer = models.TextField()
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.question[:80]
