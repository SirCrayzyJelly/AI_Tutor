from django.db import models

class QAEntry(models.Model):
    lecture_id = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.question[:80]
