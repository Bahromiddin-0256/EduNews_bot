from fastapi_admin.models import AbstractAdmin
from tortoise import fields
from tortoise.models import Model


class Admin(AbstractAdmin):
    def __str__(self):
        return f"{self.pk}#{self.username}"


class District(Model):
    name = fields.CharField(max_length=50)
    points = fields.IntField(default=0)

    schools: fields.ReverseRelation["School"]
    users: fields.ReverseRelation["User"]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class School(Model):
    district: fields.ForeignKeyRelation[District] = fields.ForeignKeyField(model_name='models.District',
                                                                           related_name='schools', on_delete='CASCADE')

    users: fields.ReverseRelation["User"]

    name = fields.CharField(max_length=50)
    points = fields.IntField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class User(Model):
    lang_code = fields.CharField(max_length=10, null=True)
    tg_id = fields.CharField(max_length=20, unique=True)
    tg_name = fields.CharField(max_length=100)
    tg_username = fields.CharField(max_length=50, null=True)
    full_name = fields.CharField(max_length=125, null=True)
    contact_number = fields.CharField(max_length=25, null=True)
    is_member = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    like_allowed = fields.BooleanField(default=False)
    post_permission = fields.BooleanField(default=True)
    registered = fields.BooleanField(default=False)
    points = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    district: fields.ForeignKeyRelation[District] = fields.ForeignKeyField(model_name='models.District',
                                                                           related_name='users', on_delete='CASCADE',
                                                                           null=True)
    school: fields.ForeignKeyRelation[School] = fields.ForeignKeyField(model_name='models.School', related_name='users',
                                                                       on_delete='CASCADE', null=True)
    posts: fields.ReverseRelation["Post"]
    liked_posts: fields.ManyToManyRelation['PostLikes']

    @property
    def mention(self, mention_text: str = None) -> str:
        if not mention_text:
            mention_text = self.full_name if self.full_name else self.tg_name
        return f"<a href='tg://user?id={self.tg_id}'>{mention_text}</a>"

    def __str__(self):
        return self.full_name if self.full_name else self.tg_name

    class Meta:
        ordering = ['-points', 'full_name']


class Post(Model):
    author: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(model_name='models.User', related_name='posts',
                                                                     on_delete='CASCADE')
    media_id = fields.CharField(max_length=100)
    media_type = fields.CharField(max_length=10)
    status = fields.CharField(max_length=20, default='waiting')
    is_published = fields.BooleanField(default=False)
    title = fields.CharField(max_length=100)
    description = fields.TextField()
    url = fields.TextField(null=True)
    facebook_url = fields.TextField(null=True)
    message_id = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    published_at = fields.DatetimeField(null=True)
    district: fields.ForeignKeyRelation[District] = fields.ForeignKeyField(model_name='models.District',
                                                                           related_name='posts')
    school: fields.ForeignKeyRelation[School] = fields.ForeignKeyField(model_name='models.School', related_name='posts')
    counter: fields.ReverseRelation['PostLikes']

    def facebook_id(self):
        if self.facebook_url:
            return self.facebook_url.split('/')[-1]
        else:
            return None

    async def context(self, fb=False) -> str:
        from core.config import settings
        if fb:
            return '\n\n'.join(
                [f"{self.title}", f"{self.description}\n", f"📍 {self.district.name},  {self.school.name}\n",
                 f"🔗 {self.url}"])
        else:
            return '\n'.join([f"<b>{self.title}</b>\n", f"<i>{self.description}</i>",
                              f"\n📍 <b>{self.district.name},  {self.school.name}</b>",
                              f"\n👉  @{settings.BOT_USERNAME}"])

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-id']


class PostLikes(Model):
    post: fields.OneToOneRelation[Post] = fields.OneToOneField(model_name='models.Post', related_name='counter')
    liked_users: fields.ManyToManyRelation[User] = fields.ManyToManyField(model_name='models.User',
                                                                          related_name='liked_posts',
                                                                          on_delete='CASCADE')
    points = fields.IntField(default=0)
    last_updated_likes = fields.IntField(default=0)


class ConnectedChannel(Model):
    user: fields.ForeignKeyRelation = fields.ForeignKeyField(model_name='models.User', related_name='connections',
                                                             on_delete='CASCADE')
    channel_id = fields.CharField(max_length=20, unique=True)
    channel_title = fields.CharField(max_length=100)
    channel_username = fields.CharField(max_length=50, null=True)
    channel_type = fields.CharField(max_length=50)
    

class MediaCategory(Model):
    objects: fields.ReverseRelation['Media']
    name = fields.CharField(max_length=100, unique=True)
    
    def __str__(self) -> str:
        return self.name
    
    
class Media(Model):
    category: fields.ForeignKeyRelation[MediaCategory] = fields.ForeignKeyField(model_name='models.MediaCategory', related_name='objects')
    title = fields.CharField(max_length=100)
    url = fields.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.title
