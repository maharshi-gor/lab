import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import markdown
import bleach

# markdown allowed tags that are not filtered by bleach

allowed_html_tags = bleach.ALLOWED_TAGS + ['p', 'pre', 'table', 'img',
                                           'h1', 'h2', 'h3', 'h4', 'h5',
                                           'h6', 'b', 'i', 'strong', 'em',
                                           'tt', 'br', 'blockquote',
                                           'code', 'ul', 'ol', 'li',
                                           'dd', 'dt', 'a', 'tr', 'td',
                                           'div', 'span', 'hr']

allowed_attrs = ['href', 'class', 'rel', 'alt', 'class', 'src']

# Create your models here.


class WebsiteSection(models.Model):
    title = models.CharField(max_length=200)
    body_markdown = models.TextField()
    body_html = models.TextField(editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    # determines for what purpose the article is used. Eg: index-header, body,
    # installation-page, getting-started-page etc
    website_position_id = models.SlugField(max_length=100,
                                           unique=True,
                                           db_index=True)

    # fixed sections cannot be added or deleted, pages can be added or deleted
    # and pages can also be listed in the nav bar
    SECTION_TYPE_CHOICES = (
        ('fixed', 'Fixed Section'),
        ('page', 'Page'),
    )
    section_type = models.CharField(max_length=100,
                                    choices=SECTION_TYPE_CHOICES,
                                    default='page')
    show_in_nav = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_section", "Can see available sections"),
            ("edit_section", "Can edit available sections"),
        )

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.body_markdown,
                                         extensions=['codehilite'])
        print(html_content)
        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(WebsiteSection, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    body_markdown = models.TextField()
    body_html = models.TextField(editable=False)
    description = models.CharField(max_length=140)
    post_date = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.body_markdown,
                                         extensions=['codehilite'])
        print(html_content)
        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(NewsPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Publication(models.Model):
    """
    Model for storing publication information.
    """
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    doi = models.CharField(max_length=100, null=True, blank=True)
    # entry type like article, inproceedings, book etc
    entry_type = models.CharField(max_length=100, null=True, blank=True)
    # name of journal in case of article or booktitle in case of
    # inproceedings
    published_in = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    year_of_publication = models.CharField(max_length=4, null=True, blank=True)
    month_of_publication = models.CharField(max_length=10, null=True, blank=True)
    bibtex = models.TextField(null=True, blank=True)
    project_url = models.CharField(max_length=200, null=True, blank=True)
    pdf = models.FileField(null=True, upload_to="publication_uploads/")
    abstract = models.TextField(null=True, blank=True)
    is_highlighted = models.BooleanField(default=False)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Publication, self).save(*args, **kwargs)

    def __str__(self):
        return self.title



class Course(models.Model):
    """
    Model for storing Course information.
    """
    title = models.CharField(max_length=200)
    acronym = models.CharField(max_length=200)
    level = models.CharField(max_length=200)
    prerequisite = models.CharField(max_length=200)
    description = models.TextField()
    syllabus = models.FileField(null=True, upload_to="course_uploads/")

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class CarouselImage(models.Model):
    """
    Model for storing image links for carousel.
    """
    image_caption = models.CharField(max_length=200)
    image_description = models.TextField(blank=True, null=True)
    target_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(max_length=200)
    display_description = models.BooleanField(default=True)

    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()

        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(CarouselImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.image_url


class Position(models.Model):
    """
    Model for defining the position of a lab member
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Model for storing more information about user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    avatar_img = models.ImageField(upload_to='avatar_images/',
                                   blank=True, null=True)
    contactNumber = models.CharField(max_length=15, blank=True, null=True)

    emailId = models.EmailField(blank=True, null=True)

    contactURL = models.URLField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    position = models.ForeignKey('Position', null=True, blank=True)

    profile_page_markdown = models.TextField(null=True, blank=True)
    profile_page_html = models.TextField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.profile_page_markdown,
                                         extensions=['codehilite'])
        # bleach is used to filter html tags like <script> for security
        self.profile_page_html = bleach.clean(html_content, allowed_html_tags,
                                              allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, full_name=instance.username,
                               profile_page_markdown="")
        instance.profile.save()


class BlogPost(models.Model):
    """
    Model to store blog posts
    """
    title = models.CharField(max_length=100, unique=True)
    identifier = models.SlugField(max_length=100, unique=True)
    body = models.TextField()
    posted = models.DateTimeField(db_index=True, auto_now_add=True)
    author = models.ForeignKey(User)
    body_html = models.TextField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        html_content = markdown.markdown(self.body,
                                         extensions=['codehilite'])
        # bleach is used to filter html tags like <script> for security
        self.body_html = bleach.clean(html_content, allowed_html_tags,
                                      allowed_attrs)
        # clear the cache
        cache.clear()

        # Call the "real" save() method.
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/blog/%i/" % self.identifier
