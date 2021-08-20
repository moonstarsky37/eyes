'''Eyes job
'''
import enum
from typing import Callable, Dict, Optional

import pydantic

from eyes.crawler.ptt import crawl_post_urls
from eyes.tasks import crawl_ptt_post


class JobType(enum.Enum):
    '''Eyes job type
    '''
    # crawler jobs
    CRAWL_PTT_LATEST_POSTS = enum.auto()


class Job(pydantic.BaseModel):
    job_type: JobType
    payload: Optional[Dict]

    @pydantic.validator('payload')
    def crawler_payload(
        cls,
        v,
        values,
        **kwargs,
    ):
        '''Crawler payload validate function
        '''
        if values['job_type'] == JobType.CRAWL_PTT_LATEST_POSTS:
            if not v:
                raise Exception("payload is required")

            for key in ['board']:
                if key not in v:
                    raise Exception(f'{key} is required in payload')

        return v


class Jobs:
    '''Job dispatcher class
    '''
    @property
    def job_map(self) -> Dict[JobType, Callable]:
        '''Return job map
        '''
        return {
            JobType.CRAWL_PTT_LATEST_POSTS: self.crawl_ptt_latest_posts,
        }

    def crawl_ptt_latest_posts(
        self,
        job: Job,
    ):
        '''Crawl latest ptt posts

        Args:
            job (Job): crawler job
        '''
        urls = crawl_post_urls(
            job.payload['board'],
            job.payload.get('n_days', None),
        )

        for url in urls:
            crawl_ptt_post.apply_async(args=[url, job.payload['board']])

    def dispatch(
        self,
        job: Job,
    ):
        '''Dispatch job

        Args:
            job (Job): Eyes job
        '''
        func = self.job_map[job.job_type]
        func(job)
