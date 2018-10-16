from django.db import models

from Base.common import deprint
from Base.error import Error
from Base.response import Ret
from Base.validator import field_validator


class Music(models.Model):
    L = {
        'name': 255,
        'singer': 100,
        'cover': 1024,
    }

    name = models.CharField(
        verbose_name='歌曲名',
        max_length=L['name'],
    )

    singer = models.CharField(
        verbose_name='歌手',
        max_length=L['singer'],
    )

    cover = models.CharField(
        verbose_name='封面',
        max_length=L['cover'],
    )

    total_comment = models.IntegerField(
        verbose_name='评论总数',
        default=0,
    )

    netease_id = models.IntegerField(
        verbose_name='网易云歌曲ID',
        default=0,
    )

    FIELD_LIST = ['name', 'singer', 'cover', 'total_comment', 'netease_id']

    @classmethod
    def _validate(cls, dict_):
        return field_validator(dict_, cls)

    @classmethod
    def create(cls, name, singer, cover, total_comment, netease_id):
        ret = cls._validate(locals())
        if ret.error is not Error.OK:
            return ret

        ret = cls.get_music_by_netease_id(netease_id)
        if ret.error is Error.OK:
            return ret

        try:
            o_music = cls(
                name=name,
                singer=singer,
                cover=cover,
                total_comment=total_comment,
                netease_id=netease_id,
            )
            o_music.save()
        except Exception as err:
            deprint(str(err))
            return Ret(Error.ERROR_CREATE_MUSIC)

        return Ret(o_music)

    @classmethod
    def get_music_by_netease_id(cls, netease_id):
        try:
            o_music = cls.objects.get(netease_id=netease_id)
        except cls.DoesNotExist as err:
            deprint(str(err))
            return Ret(Error.NOT_FOUND_MUSIC)
        return Ret(o_music)

    @classmethod
    def get_music_list(cls, end, count=10):
        if count > 10 or count <= 0:
            count = 10

        last = cls.objects.count()

        # start = -1: start = last - 10 or start = 0
        if end > last or end == -1:
            end = last
        if end - count < 0:
            count = end
        start = end - count

        music_list = []
        for o_music in cls.objects.all()[start:end]:
            music_list.insert(0, o_music.to_dict())

        return Ret(dict(
            music_list=music_list,
            next_id=start
        ))

    def to_dict(self):
        return dict(
            id=self.pk,
            name=self.name,
            singer=self.singer,
            cover=self.cover,
            total_comment=self.total_comment,
            netease_id=self.netease_id,
        )