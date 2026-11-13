
import pytest

from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def create_student(**kwargs):
    return Student(student_id="S001", **kwargs)


def create_course(**kwargs):
    course_data = {
        "code": "CS101",
        "credit_hours": 3,
        "capacity": 30
    }
    course_data.update(kwargs)
    return Course(**course_data)


# --------------------------------------------------
# B4: Control Flow Graph Path Tests
# --------------------------------------------------

def test_wb_p1_negative_dues():
    student = create_student(outstanding_dues=-1)
    course = create_course()

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


def test_wb_p2_invalid_capacity():
    student = create_student()
    course = create_course(capacity=0)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_wb_negative_enrollment():
    student = create_student()
    course = create_course(enrolled=-1)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_wb_enrollment_exceeds_capacity():
    student = create_student()
    course = create_course(capacity=1, enrolled=2)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_wb_p3_dues_block():
    student = create_student(outstanding_dues=1001)
    course = create_course()

    result = registration_decision(student, course)

    assert result == "DUES_BLOCK"


def test_wb_p4_already_registered():
    student = create_student(registered_courses={"CS101"})
    course = create_course()

    result = registration_decision(student, course)

    assert result == "ALREADY_REGISTERED"


def test_wb_p5_missing_prerequisites():
    student = create_student()
    course = create_course(prerequisites={"CS100"})

    result = registration_decision(student, course)

    assert result == "PREREQUISITES_MISSING"


def test_wb_p6_credit_limit():
    student = create_student(current_credits=15)
    course = create_course(credit_hours=3)

    result = registration_decision(student, course)

    assert result == "CREDIT_LIMIT"


def test_wb_p7_waitlisted():
    student = create_student()
    course = create_course(capacity=1, enrolled=1)

    result = registration_decision(student, course)

    assert result == "WAITLISTED"


def test_wb_p8_registered():
    student = create_student()
    course = create_course()

    result = registration_decision(student, course)

    assert result == "REGISTERED"


# --------------------------------------------------
# B3: Condition Coverage and MC/DC Tests
# --------------------------------------------------

def test_wb_mcdc_baseline():
    student = create_student()
    course = create_course(capacity=1, enrolled=0)

    result = registration_decision(student, course)

    assert result == "REGISTERED"


def test_wb_mcdc_condition_c1():
    student = create_student()
    course = create_course(capacity=1, enrolled=-1)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_wb_mcdc_condition_c2():
    student = create_student()
    course = create_course(capacity=1, enrolled=2)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


def test_wb_mcdc_condition_c3():
    student = create_student()
    course = create_course(capacity=0, enrolled=0)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


# --------------------------------------------------
# Helper Function Tests
# --------------------------------------------------

def test_wb_credit_limit_valid():
    result = check_credit_limit(10, 3)

    assert result is True


def test_wb_credit_limit_exactly_18():
    result = check_credit_limit(17, 1)

    assert result is True


def test_wb_credit_limit_exceeded():
    result = check_credit_limit(16, 3)

    assert result is False


def test_wb_invalid_current_credits():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 3)


def test_wb_invalid_new_credits():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(10, 5)


def test_wb_no_prerequisites():
    result = prerequisites_satisfied(set(), set())

    assert result is True


def test_wb_all_prerequisites_satisfied():
    completed = {"CS100", "CS101"}
    required = {"CS100", "CS101"}

    result = prerequisites_satisfied(completed, required)

    assert result is True


def test_wb_partial_prerequisites():
    completed = {"CS100"}
    required = {"CS100", "CS101"}

    result = prerequisites_satisfied(completed, required)

    assert result is False


# --------------------------------------------------
# Registration Function Tests
# --------------------------------------------------

def test_wb_register_course_success():
    student = create_student()
    course = create_course()

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS101" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 1


def test_wb_register_course_waitlist():
    student = create_student()
    course = create_course(capacity=1, enrolled=1)

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert "S001" in course.waitlist


# --------------------------------------------------
# Withdrawal Function Tests
# --------------------------------------------------

def test_wb_withdraw_not_registered():
    student = create_student()
    course = create_course()

    result = withdraw_course(student, course)

    assert result is False


def test_wb_withdraw_registered():
    student = create_student(
        registered_courses={"CS101"},
        current_credits=3
    )
    course = create_course(enrolled=5)

    result = withdraw_course(student, course)

    assert result is True
    assert "CS101" not in student.registered_courses
    assert student.current_credits == 0
    assert course.enrolled == 4


def test_wb_positive_dues_block():
    student = create_student(outstanding_dues=1)
    course = create_course()

    result = registration_decision(student, course)

    assert result == "DUES_BLOCK"
