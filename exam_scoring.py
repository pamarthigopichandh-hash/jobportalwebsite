# jobapp/exam_scoring.py
from django.utils import timezone
from jobapp.models import ExamAttempt, ExamAnswer, ExamQuestion, ExamOption

def score_exam_attempt(attempt: ExamAttempt, submitted_answers: dict):
    """
    Scores an exam attempt and updates ExamAttempt and JobApplication.
    
    submitted_answers: dict mapping question.id -> option.id
    Example: {1: 3, 2: 7}  # question_id : selected option_id
    """
    total_score = 0

    for question_id, option_id in submitted_answers.items():
        try:
            question = ExamQuestion.objects.get(id=question_id)
            selected_option = question.options.get(id=option_id)

            # Save the user's answer
            ExamAnswer.objects.create(
                attempt=attempt,
                question=question,
                answer_text=selected_option.text,
                is_correct=selected_option.is_correct
            )

            if selected_option.is_correct:
                total_score += 1  # 1 point per correct answer

        except ExamQuestion.DoesNotExist:
            continue
        except ExamOption.DoesNotExist:
            continue

    # Update the ExamAttempt
    attempt.score = total_score
    attempt.status = "Passed" if total_score >= len(attempt.application.job.exam_questions.all()) * 0.5 else "Failed"
    attempt.completed_at = timezone.now()
    attempt.save()

    # Update the JobApplication record
    application = attempt.application
    application.exam_score = total_score
    application.exam_completed = True
    application.final_score = total_score  # optional if you want final_score same as exam_score
    application.save()

    return total_score