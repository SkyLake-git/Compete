from abc import *

class SubmissionResult:
    @abstractmethod
    def is_accepted(self):
        pass

class Submission:
    created: int
    problem: str
    time_consumption: float
    result: SubmissionResult
    memory_consumption: float

class SubmissionOption:
    pass

class SubmissionHandler:

    @abstractmethod
    def submit(self, content: str, option: SubmissionOption) -> None:
        pass

    @abstractmethod
    def can_fetch_submissions(self) -> bool:
        pass

    @abstractmethod
    def fetch_submissions(self) -> list[Submission]:
        pass