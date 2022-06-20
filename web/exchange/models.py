from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
from os.path import basename,isfile, join
from os import remove

class ConfFlags(models.Model):
  name = models.CharField(max_length=50)
  flags = models.CharField(max_length=120)
  participantType = models.IntegerField()
  def __str__(self):
    return self.name

class ConfAuth(models.Model):
  confName = models.CharField(max_length=120)
  confExt = models.CharField(max_length=50)
  confDescription = models.CharField(max_length=250)
  userName = models.CharField(max_length=120)
  key = models.CharField(max_length=100)
  role = models.ForeignKey(ConfFlags,null=True,on_delete=models.SET_NULL)
  timeStart = models.DateTimeField(default=timezone.now)

class Conference(models.Model):
  name = models.CharField(max_length=120)
  extension = models.CharField(max_length=50)
  description = models.CharField(max_length=250)
  timeStart = models.DateTimeField(default=timezone.now)
  duration_minutes = models.IntegerField(default=180)
  def __str__(self):
    return self.name
  
class ConfUser(models.Model):
  name = models.CharField(max_length=120)
  key = models.CharField(max_length=32, null=True, blank=True)
  ip = models.CharField(max_length=15, null=True, blank=True)
  registered_user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
  def __str__(self):
    return self.name
  
class Assignment(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4)
  user = models.ForeignKey(ConfUser,on_delete=models.CASCADE)
  conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
  flags = models.ForeignKey(ConfFlags, null=True, on_delete=models.SET_NULL)
  def __str__(self):
    return self.user.name + '@' + self.conference.name
  
  def getJoinURL():
    auth = Authntication(self)
    auth.save()
    return auth.id
    
  
class Authentication(models.Model):
  assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
  id = models.UUIDField(primary_key=True,default=uuid.uuid4)
  
class FixedEndpoint(models.Model):
    ip = models.CharField(max_length=15)
    display_name = models.CharField(max_length=255)
    name = models.CharField(max_length=128)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    def __str__(self):
        return self.name + " (" + self.ip +")" + self.conference.name
  
class ParamsCache(models.Model):
    name = models.CharField(max_length=64,unique=True)
    data = models.TextField()
    def __srt__(self):
        return self.name
    
class Settings(models.Model):
    name = models.CharField(max_length=64,primary_key=True,unique=True)
    data = models.TextField()
    def __str__(self):
        return self.name
      
class Recording(models.Model):
  name = models.CharField(max_length=128)
  description = models.TextField(null=True, blank=True)
  conference = models.ForeignKey(Conference, null=True, on_delete=models.SET_NULL)
  status = models.PositiveSmallIntegerField()
  startDate = models.DateTimeField()
  duration = models.DurationField(null=True,blank=True)
  fname = models.CharField(max_length=48)  
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['fname','conference'], name='unique_record')
      ]
    
  def delete(self):
    rec_path = Settings.objects.get(name='record_path').data
    path = join(rec_path, 'published', self.fname)
    print("Recording will be deleted: " + path)
    if isfile(path):
      remove(path)      
    super().delete()
    
  def __str__(self):
    return self.fname
    

def get_upload_directory(instance, filename):
    return "assets/{0}/{1}/{2}".format(instance.conference.extension,instance.user.id, filename)   

class Asset(models.Model):
    name = models.CharField(max_length=128,blank=True)
    fileField = models.FileField(upload_to=get_upload_directory)
    date = models.DateTimeField(auto_now_add=True)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def get_base_name(self):
        return basename(self.fileField.path)
    def __str__(self):
        return self.get_base_name(self)
    
    def delete(self):
        self.fileField.storage.delete(self.fileField.name)
        super().delete()
