import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Job:
    id: str
    task_name: str
    params: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0

class JobProcessor:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.task_registry: Dict[str, Callable] = {}
        self.queue: List[str] = []
        self.is_processing = False
        self.max_concurrent_jobs = 1  # V0: Process one job at a time
        
    def register_task(self, task_name: str, task_func: Callable):
        """Register a task function"""
        self.task_registry[task_name] = task_func
        logger.info(f"Registered task: {task_name}")
    
    def create_job(self, task_name: str, params: Dict[str, Any]) -> str:
        """Create a new job and add it to the queue"""
        if task_name not in self.task_registry:
            raise ValueError(f"Unknown task: {task_name}")
        
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            task_name=task_name,
            params=params
        )
        
        self.jobs[job_id] = job
        self.queue.append(job_id)
        
        logger.info(f"Created job {job_id} for task {task_name}")
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self._process_queue())
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        return list(self.jobs.values())
    
    def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get jobs by status"""
        return [job for job in self.jobs.values() if job.status == status]
    
    async def _process_queue(self):
        """Process jobs in the queue"""
        if self.is_processing:
            return
        
        self.is_processing = True
        logger.info("Started job queue processing")
        
        try:
            while self.queue:
                job_id = self.queue.pop(0)
                job = self.jobs.get(job_id)
                
                if not job or job.status != JobStatus.PENDING:
                    continue
                
                await self._process_job(job)
                
                # Small delay between jobs
                await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error in queue processing: {e}")
        
        finally:
            self.is_processing = False
            logger.info("Stopped job queue processing")
    
    async def _process_job(self, job: Job):
        """Process a single job"""
        try:
            logger.info(f"Processing job {job.id}: {job.task_name}")
            
            # Update job status
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now()
            job.progress = 0.1
            
            # Get task function
            task_func = self.task_registry[job.task_name]
            
            # Execute task
            if asyncio.iscoroutinefunction(task_func):
                result = await task_func(**job.params)
            else:
                result = task_func(**job.params)
            
            # Update job with result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result = result
            job.progress = 1.0
            
            logger.info(f"Job {job.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            
            # Update job with error
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)
            job.progress = 0.0
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status summary"""
        job = self.jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        return {
            "id": job.id,
            "task_name": job.task_name,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "result": job.result,
            "error": job.error
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return {
            "is_processing": self.is_processing,
            "queue_length": len(self.queue),
            "total_jobs": len(self.jobs),
            "pending_jobs": len(self.get_jobs_by_status(JobStatus.PENDING)),
            "processing_jobs": len(self.get_jobs_by_status(JobStatus.PROCESSING)),
            "completed_jobs": len(self.get_jobs_by_status(JobStatus.COMPLETED)),
            "failed_jobs": len(self.get_jobs_by_status(JobStatus.FAILED))
        }

# Global instance
job_processor = JobProcessor()

# Video processing tasks
async def process_video_task(meeting_id: str) -> Dict[str, Any]:
    """Task to process a video from start to finish"""
    from video_processor import process_video_complete
    from ai_generator import generate_all_content
    
    try:
        # Step 1: Process video (download, extract metadata, generate transcript, upload)
        video_result = await process_video_complete(meeting_id)
        
        # Step 2: Generate AI content from transcript
        transcript = video_result["transcript"]
        title = video_result["metadata"]["title"]
        
        ai_content = await generate_all_content(transcript, title)
        
        # Combine results
        result = {
            "meeting_id": meeting_id,
            "video": video_result,
            "ai_content": ai_content,
            "pipeline_status": "completed"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Video processing task failed for {meeting_id}: {e}")
        raise

# Register tasks
job_processor.register_task("process_video", process_video_task)

# Convenience functions
def create_video_processing_job(meeting_id: str) -> str:
    """Create a job to process a video"""
    return job_processor.create_job("process_video", {"meeting_id": meeting_id})

def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get job status"""
    return job_processor.get_job_status(job_id)

def get_queue_status() -> Dict[str, Any]:
    """Get queue status"""
    return job_processor.get_queue_status()