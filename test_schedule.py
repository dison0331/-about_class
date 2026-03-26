"""
教务系统调课软件测试脚本
"""

from course_schedule import Course, ScheduleManager


def test_basic_operations():
    """测试基本操作"""
    print("=" * 50)
    print("测试基本操作")
    print("=" * 50)
    
    manager = ScheduleManager()
    
    # 测试添加课程
    print("\n1. 测试添加课程...")
    course1 = Course("MATH101", "高等数学", "张老师", 1, 1, 2)
    course2 = Course("ENG101", "大学英语", "李老师", 1, 3, 2)
    course3 = Course("CS101", "计算机基础", "王老师", 2, 1, 2)
    
    assert manager.add_course(course1), "添加课程1失败"
    assert manager.add_course(course2), "添加课程2失败"
    assert manager.add_course(course3), "添加课程3失败"
    print("✅ 课程添加成功")
    
    # 测试冲突检测
    print("\n2. 测试冲突检测...")
    conflict_course = Course("MATH102", "线性代数", "张老师", 1, 2, 1)
    has_conflict, conflicts = manager.check_conflict(conflict_course)
    assert has_conflict, "应该检测到冲突"
    print(f"✅ 冲突检测成功: {conflicts[0]}")
    
    # 测试显示课表
    print("\n3. 测试显示课表...")
    manager.display_schedule(day=1)
    
    # 测试调课
    print("\n4. 测试调课...")
    success, message = manager.modify_course("MATH101", new_day=3, new_period=5)
    assert success, f"调课失败: {message}"
    print(f"✅ 调课成功: {message}")
    
    # 测试调课冲突
    print("\n5. 测试调课冲突...")
    success, message = manager.modify_course("MATH101", new_day=1, new_period=1)
    assert not success, "应该检测到调课冲突"
    print(f"✅ 调课冲突检测成功: {message}")
    
    # 测试删除课程
    print("\n6. 测试删除课程...")
    assert manager.remove_course("ENG101"), "删除课程失败"
    print("✅ 课程删除成功")
    
    # 测试保存和加载
    print("\n7. 测试保存和加载...")
    manager.save_to_file("test_schedule.json")
    
    new_manager = ScheduleManager()
    new_manager.load_from_file("test_schedule.json")
    assert len(new_manager.courses) == 2, "加载后课程数量不正确"
    print("✅ 保存和加载成功")
    
    print("\n" + "=" * 50)
    print("所有测试通过!")
    print("=" * 50)


def test_teacher_schedule():
    """测试老师课表功能"""
    print("\n" + "=" * 50)
    print("测试老师课表功能")
    print("=" * 50)
    
    manager = ScheduleManager()
    
    # 添加多个课程
    courses = [
        Course("MATH101", "高等数学", "张老师", 1, 1, 2),
        Course("PHY101", "大学物理", "张老师", 2, 5, 2),
        Course("ENG101", "大学英语", "李老师", 1, 3, 2),
        Course("CS101", "计算机基础", "王老师", 3, 1, 3),
    ]
    
    for course in courses:
        manager.add_course(course)
    
    # 查看老师课表
    print("\n查看张老师的课表:")
    manager.display_schedule(teacher="张老师")
    
    print("\n查看李老师的课表:")
    manager.display_schedule(teacher="李老师")


def test_conflict_scenarios():
    """测试各种冲突场景"""
    print("\n" + "=" * 50)
    print("测试冲突场景")
    print("=" * 50)
    
    manager = ScheduleManager()
    
    # 场景1: 完全重叠
    print("\n场景1: 完全重叠")
    course1 = Course("A", "课程A", "老师1", 1, 1, 2)
    course2 = Course("B", "课程B", "老师1", 1, 1, 2)
    
    manager.add_course(course1)
    has_conflict, conflicts = manager.check_conflict(course2)
    assert has_conflict, "应该检测到完全重叠冲突"
    print(f"✅ 检测到冲突: {conflicts[0]}")
    
    # 场景2: 部分重叠
    print("\n场景2: 部分重叠")
    course3 = Course("C", "课程C", "老师1", 1, 2, 2)
    has_conflict, conflicts = manager.check_conflict(course3)
    assert has_conflict, "应该检测到部分重叠冲突"
    print(f"✅ 检测到冲突: {conflicts[0]}")
    
    #