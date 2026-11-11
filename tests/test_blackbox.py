import pytest

from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course,
)


def make_student(**kwargs):
    """Create a fresh student for each test."""
    defaults = {
        "student_id": "S001",
        "completed_courses": set(),
        "current_credits": 0,
        "outstanding_dues": 0,
        "registered_courses": set(),
    }
    defaults.update(kwargs)
    return Student(**defaults)


def make_course(**kwargs):
    """Create a fresh course for each test."""
    defaults = {
        "code": "CS201",
        "credit_hours": 3,
        "capacity": 30,
        "enrolled": 0,
        "prerequisites": set(),
        "waitlist": [],
    }
    defaults.update(kwargs)
    return Course(**defaults)
# ==========================
# A1: EQUIVALENCE CLASS PARTITIONING
# ==========================

@pytest.mark.parametrize(
    "current, new, expected",
    [
        pytest.param(15, 3, True, id="ECP-01"),
    ],
)
def test_ecp_valid_credit_limit(current, new, expected):
    assert check_credit_limit(current, new) == expected


@pytest.mark.parametrize(
    "current, new",
    [
        pytest.param(-1, 3, id="ECP-02"),
        pytest.param(19, 3, id="ECP-03"),
        pytest.param(10, 0, id="ECP-04"),
        pytest.param(10, 5, id="ECP-05"),
    ],
)
def test_ecp_invalid_credit_values(current, new):
    with pytest.raises(ValueError):
        check_credit_limit(current, new)


def test_ecp_06_zero_dues():
    student = make_student()
    course = make_course()

    assert registration_decision(student, course) == "REGISTERED"


def test_ecp_07_positive_dues():
    student = make_student(outstanding_dues=1)
    course = make_course()

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_ecp_08_negative_dues():
    student = make_student(outstanding_dues=-1)
    course = make_course()

    with pytest.raises(ValueError):
        registration_decision(student, course)


def test_ecp_09_all_prerequisites_completed():
    assert prerequisites_satisfied(
        {"CS101", "MATH101"},
        {"CS101", "MATH101"}
    ) is True


def test_ecp_10_no_prerequisites_required():
    assert prerequisites_satisfied(set(), set()) is True


def test_ecp_11_one_prerequisite_missing():
    assert prerequisites_satisfied(
        {"CS101"},
        {"CS101", "MATH101"}
    ) is False


def test_ecp_12_all_prerequisites_missing():
    assert prerequisites_satisfied(
        set(),
        {"CS101", "MATH101"}
    ) is False


def test_ecp_13_course_has_free_seat():
    student = make_student()
    course = make_course(enrolled=29)

    assert registration_decision(student, course) == "REGISTERED"


def test_ecp_14_course_is_full():
    student = make_student()
    course = make_course(enrolled=30)

    assert registration_decision(student, course) == "WAITLISTED"


def test_ecp_15_already_registered():
    student = make_student(
        registered_courses={"CS201"}
    )
    course = make_course()

    assert registration_decision(student, course) == "ALREADY_REGISTERED"
# ==========================
# A2: BOUNDARY VALUE ANALYSIS
# ==========================

@pytest.mark.parametrize(
    "current, new, expected",
    [
        pytest.param(0, 1, True, id="BVA-01"),
        pytest.param(1, 2, True, id="BVA-02"),
        pytest.param(14, 3, True, id="BVA-03"),
        pytest.param(15, 3, True, id="BVA-04"),
        pytest.param(16, 3, False, id="BVA-05"),
        pytest.param(18, 1, False, id="BVA-06"),
    ],
)
def test_bva_credit_limit(current, new, expected):
    assert check_credit_limit(current, new) == expected


@pytest.mark.parametrize(
    "current, new",
    [
        pytest.param(-1, 1, id="BVA-07"),
        pytest.param(19, 1, id="BVA-08"),
        pytest.param(0, 0, id="BVA-09"),
        pytest.param(0, 5, id="BVA-10"),
    ],
)
def test_bva_invalid_credit_boundaries(current, new):
    with pytest.raises(ValueError):
        check_credit_limit(current, new)


@pytest.mark.parametrize(
    "dues, expected",
    [
        pytest.param(0, "REGISTERED", id="BVA-11"),
        pytest.param(1, "DUES_BLOCK", id="BVA-12"),
    ],
)
def test_bva_dues_boundary(dues, expected):
    student = make_student(outstanding_dues=dues)
    course = make_course()

    assert registration_decision(student, course) == expected


@pytest.mark.parametrize(
    "enrolled, expected",
    [
        pytest.param(29, "REGISTERED", id="BVA-13"),
        pytest.param(30, "WAITLISTED", id="BVA-14"),
        pytest.param(31, "ValueError", id="BVA-15"),
    ],
)
def test_bva_capacity_boundary(enrolled, expected):
    student = make_student()
    course = make_course(enrolled=enrolled)

    if expected == "ValueError":
        with pytest.raises(ValueError):
            registration_decision(student, course)
    else:
        assert registration_decision(student, course) == expected
# ==========================
# A3: DECISION TABLE TESTING
# ==========================

def test_dt_01_dues_block():
    student = make_student(outstanding_dues=1)
    course = make_course()

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_dt_02_already_registered():
    student = make_student(registered_courses={"CS201"})
    course = make_course()

    assert registration_decision(student, course) == "ALREADY_REGISTERED"


def test_dt_03_prerequisites_missing():
    student = make_student(completed_courses={"CS101"})
    course = make_course(prerequisites={"CS101", "MATH101"})

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


def test_dt_04_credit_limit_exceeded():
    student = make_student(current_credits=16)
    course = make_course(credit_hours=3)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


def test_dt_05_course_full():
    student = make_student()
    course = make_course(enrolled=30)

    assert registration_decision(student, course) == "WAITLISTED"


def test_dt_06_seat_available():
    student = make_student()
    course = make_course(enrolled=29)

    assert registration_decision(student, course) == "REGISTERED"


def test_dt_07_dues_priority_over_duplicate():
    student = make_student(
        outstanding_dues=1,
        registered_courses={"CS201"}
    )
    course = make_course()

    assert registration_decision(student, course) == "DUES_BLOCK"


def test_dt_08_duplicate_priority_over_prerequisites():
    student = make_student(
        registered_courses={"CS201"},
        completed_courses=set()
    )
    course = make_course(
prerequisites={"CS101", "MATH101"}      
    )

    assert registration_decision(student, course) == "ALREADY_REGISTERED"
prerequisites={"CS101", "MATH101"}
def test_dt_08_duplicate_priority_over_prerequisites():
    student = make_student(
        registered_courses={"CS201"},
        completed_courses=set()
    )
    course = make_course(
        prerequisites={"CS101", "MATH101"}
    )

    assert registration_decision(student, course) == "ALREADY_REGISTERED"
# ==========================
# A4: REGISTRATION AND WITHDRAWAL STATE TESTS
# ==========================

def test_successful_registration_updates_state():
    student = make_student()
    course = make_course()

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS201" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 1


def test_failed_registration_does_not_change_state():
    student = make_student(outstanding_dues=1)
    course = make_course()

    original_credits = student.current_credits
    original_courses = student.registered_courses.copy()
    original_enrolled = course.enrolled
    original_waitlist = course.waitlist.copy()

    result = register_course(student, course)

    assert result == "DUES_BLOCK"
    assert student.current_credits == original_credits
    assert student.registered_courses == original_courses
    assert course.enrolled == original_enrolled
    assert course.waitlist == original_waitlist


def test_withdrawal_updates_student_and_course_state():
    student = make_student(
        current_credits=3,
        registered_courses={"CS201"}
    )
    course = make_course(enrolled=1)

    result = withdraw_course(student, course)

    assert result is True
    assert "CS201" not in student.registered_courses
    assert student.current_credits == 0
    assert course.enrolled == 0


def test_withdrawal_without_registration_changes_nothing():
    student = make_student()
    course = make_course(enrolled=5)

    result = withdraw_course(student, course)

    assert result is False
    assert student.registered_courses == set()
    assert student.current_credits == 0
    assert course.enrolled == 5
