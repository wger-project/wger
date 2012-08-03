from django.db import models


class ExerciseCategory(models.Model):
    """Model for an exercise category
    """
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name

class Exercise(models.Model):
    """Model for an exercise
    """
    category = models.ForeignKey(ExerciseCategory)
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name

class ExerciseComment(models.Model):
    """Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise)
    comment = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.comment


