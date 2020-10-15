from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from django.utils.html import strip_tags

# Create your models here.

class Category(models.Model):
    """
    django要求模型必须继承models.Model类。
    Category只需要一个简单的分类名name就可以了。
    CharField指定了分类名name的数据类型，CharField是字符型
    CharField的max_length参数指定其最大长度，超过这个长度的分类名就不能被存入数据库
    当然django还为我们提供了多种其他的数据类型，如日期时间类型DateTimeField、证书类型InterField等等。
    django内置的全部类型可查看文档
    https://docs.djangoproject.com/en/2.2/ref/models/fields/#field-types
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    标签Tag也比较简单，和Category一样。
    再次强调一定要继承models.Model类！
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Post(models.Model):
    """
    文章的数据库表稍微复杂一点，主要是设计的字段更多
    """

    #文章标题
    title = models.CharField('标题', max_length=70)

    #文章正文，我们是用来 TextField
    #存储比较短的字符串可以使用CharField，但对于文章的正文来说可能会使一大段文本，因此使用TextField来存储大段文本。
    body = models.TextField('正文')

    #这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField类型
    created_time = models.DateTimeField('创建时间')
    modified_time = models.DateTimeField('修改时间')

    #文章摘要，可以没有文章摘要，但默认情况下CharField要求我们必须存入数据，否则就会报错。
    #指定CharField的blan=True参数值后就可以允许空值了。
    excerpt = models.CharField('摘要', max_length=200,blank=True)

    #这是分类与标签，分类与标签的模型我们已经定义在上面。
    #我们在这里吧文章对应的数据库和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    #规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是ForeignKey,即一
    #对多的关联关系。且自django2.0以后，ForeignKey必须传入一个on_delete参数用来指定当关联的
    #数据被删除时，被关联的数据的行为，假设当某个分类被删除时候，该分类下全部文章也同时被删除，因此
    #对于标签来说，一篇文章可以对应多个标签，同一个标签下也可能有多篇文章，所以使用
    #ManyToManyField，表名这是多对多的关联关系
    #同时文章没有标签时候，指定blank = True。
    category = models.ForeignKey(Category, verbose_name='分类',on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签',blank=True)

    #文章作者，这里User是从django.contrib.auth.models导入
    #django.contrib.auth是django内置的应用，专用于处理网站用户的注册、登录等流程，User是django已经写好的用户模型
    #这里我们通过ForeignKey把文章和User关联了起来。
    #因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此是一度多的关联关系，和Category类似
    author = models.ForeignKey(User, verbose_name='作者',on_delete=models.CASCADE)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
    def __str__(self):
        return self.title

    created_time = models.DateTimeField('创建时间', default=timezone.now)

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()

        #首先实例化一个 Markdown类，用于渲染 body的文本
        #由于摘要并不需要生成文章目录，所以去掉了目录拓展
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])

        #先将 Markdown 文本渲染成 HTML 文本
        #strip_tags 去掉 HTML 文本的全部 HTML 标签
        #从文本摘取前 54 个字符赋给 excerpt
        self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args, **kwargs)

    # 自定义 get_absolute_url 方法
    # 记得从 django.urls 中导入 reverse 函数
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk':self.pk})