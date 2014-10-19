from django.db import models

class Slide(models.Model):
    title = models.CharField(max_length=128)
    pub_date = models.DateTimeField()
    filename = models.CharField(max_length=64) 
    pdf_text_content = models.TextField(max_length=2048, blank=True)
    lecture = models.ForeignKey('Lecture')
    confusing = models.ManyToManyField("AuroraUser.aurorauser", related_name="confusing", blank=True)
    important = models.ManyToManyField("AuroraUser.aurorauser", related_name="important", blank=True)
    liked = models.ManyToManyField("AuroraUser.aurorauser", related_name="liked", blank=True)
    tags = models.CharField(max_length=128, blank=True)
    
    class Meta:
        unique_together = (("lecture", "filename"),)
        ordering = ['pub_date']
    
    def __unicode__(self):
        return str(self.lecture.course.short_title) + ' | ' + str(self.id) + ' | ' + self.title

    def set_marker(self, user, marker, value):
        if value:
            getattr(self, marker).add(user)
        else:
            getattr(self, marker).remove(user)
    
    def get_marker_count(self, marker):
        return getattr(self, marker).count()
    
    # get_thumbnail_image
    # get_medium_image
    # get_pdf_image
    
class Lecture(models.Model):
    course = models.ForeignKey("Course.course")
    id_relative = models.IntegerField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start']
    
    def __unicode__(self):
        return str(self.course.short_title) + " | " + str(self.id_relative)
        
    def save(self):
        self.id_relative = Lecture.objects.filter(course=self.course).count() +1
        super(Lecture, self).save()
    
    
class Stream(models.Model):
    lecture = models.OneToOneField('Lecture')
    type = models.CharField(max_length=32)
    url = models.CharField(max_length=512)
    clipname = models.CharField(max_length=512)
    offset = models.IntegerField()
    
    def __unicode__(self):
        return str(self.lecture.course.short_title) + " | " + str(self.lecture.id)
