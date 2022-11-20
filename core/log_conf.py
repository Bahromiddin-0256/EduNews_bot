import logging

from core.config import settings

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO if settings.DEBUG else logging.ERROR,
                    )
