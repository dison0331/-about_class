"""
教务系统调课软件
功能：显示课表、调课、冲突检测
"""

from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional
import json


class Course:
    """课程类，存储课程基本信息"""

    def __init__(self, course_id: str, name: str, teacher: str,
                 day: int, period: int, duration: int = 1):
        self.course_id = course_id
        self.name = name
        self.teacher = teacher
        self.day = day  # 1-7，1表示周一，7表示周日
        self.period = period  # 开始节次，如1表示第1节开始
        self.duration = duration  # 课程持续节次
        
    def get_periods(self) -> List[int]:
        """获取课程占用的所有节次"""
        return list(range(self.period, self.period + self.duration))
    
    def __repr__(self):
        return f"Course({self.name}, {self.teacher}, 周{self.day}, {self.period}-{self.period + self.duration - 1}节)"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'course_id': self.course_id,
            'name': self.name,
            'teacher': self.teacher,
            'day': self.day,
            'period': self.period,
            'duration': self.duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Course':
        """从字典创建课程对象"""
        return cls(
            data['course_id'],
            data['name'],
            data['teacher'],
            data['day'],
            data['period'],
            data.get('duration', 1)
        )


class ScheduleManager:
    """课表管理器"""
    
    def __init__(self):
        self.courses: Dict[str, Course] = {}  # 课程ID到课程对象的映射
        self.teacher_schedule: Dict[str, Dict[int, Set[int]]] = {}  # 老师到时间的映射
        self.classroom_schedule: Dict[str, Dict[int, Set[int]]] = {}  # 教室到时间的映射
        
    def add_course(self, course: Course) -> bool:
        """添加课程，检查是否冲突"""
        has_conflict, _ = self.check_conflict(course)
        if has_conflict:
            return False

        self.courses[course.course_id] = course

        # 更新老师课表
        if course.teacher not in self.teacher_schedule:
            self.teacher_schedule[course.teacher] = {}
        if course.day not in self.teacher_schedule[course.teacher]:
            self.teacher_schedule[course.teacher][course.day] = set()

        for period in course.get_periods():
            self.teacher_schedule[course.teacher][course.day].add(period)

        return True
    
    def remove_course(self, course_id: str) -> bool:
        """移除课程"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        
        # 从老师课表中移除
        if course.teacher in self.teacher_schedule:
            if course.day in self.teacher_schedule[course.teacher]:
                for period in course.get_periods():
                    self.teacher_schedule[course.teacher][course.day].discard(period)
        
        del self.courses[course_id]
        return True
    
    def check_conflict(self, course: Course, exclude_course_id: str = None) -> Tuple[bool, List[str]]:
        """检查课程是否冲突，返回(是否冲突, 冲突信息列表)"""
        conflicts = []
        
        # 检查老师时间冲突
        if course.teacher in self.teacher_schedule:
            if course.day in self.teacher_schedule[course.teacher]:
                for period in course.get_periods():
                    if period in self.teacher_schedule[course.teacher][course.day]:
                        # 检查是否是同一课程（用于修改时的检查）
                        conflict_course = self.find_course_by_teacher_time(
                            course.teacher, course.day, period
                        )
                        if conflict_course and conflict_course.course_id != exclude_course_id:
                            conflicts.append(
                                f"老师 {course.teacher} 在周{course.day} 第{period}节已有课程: {conflict_course.name}"
                            )
        
        return (len(conflicts) > 0, conflicts)
    
    def find_course_by_teacher_time(self, teacher: str, day: int, period: int) -> Optional[Course]:
        """根据老师和时间查找课程"""
        for course in self.courses.values():
            if (course.teacher == teacher and 
                course.day == day and 
                period in course.get_periods()):
                return course
        return None
    
    def modify_course(self, course_id: str, new_day: int = None, new_period: int = None) -> Tuple[bool, str]:
        """修改课程时间"""
        if course_id not in self.courses:
            return (False, "课程不存在")
        
        course = self.courses[course_id]
        
        if new_day is None and new_period is None:
            return (False, "没有指定修改内容")
        
        # 创建临时课程对象检查冲突
        temp_day = new_day if new_day is not None else course.day
        temp_period = new_period if new_period is not None else course.period
        
        temp_course = Course(
            course.course_id,
            course.name,
            course.teacher,
            temp_day,
            temp_period,
            course.duration
        )
        
        has_conflict, conflicts = self.check_conflict(temp_course, exclude_course_id=course_id)
        
        if has_conflict:
            conflict_msg = "\n".join(conflicts)
            return (False, f"调课冲突:\n{conflict_msg}")
        
        # 移除旧课程，添加新课程
        self.remove_course(course_id)
        new_course = Course(
            course.course_id,
            course.name,
            course.teacher,
            temp_day,
            temp_period,
            course.duration
        )
        self.add_course(new_course)
        
        return (True, "调课成功")
    
    def get_courses_by_day(self, day: int) -> List[Course]:
        """获取某天的所有课程"""
        return [course for course in self.courses.values() if course.day == day]
    
    def get_courses_by_teacher(self, teacher: str) -> List[Course]:
        """获取某老师的所有课程"""
        return [course for course in self.courses.values() if course.teacher == teacher]
    
    def display_schedule(self, day: int = None, teacher: str = None):
        """显示课表"""
        if day:
            courses = self.get_courses_by_day(day)
            print(f"\n=== 周{day} 课表 ===")
        elif teacher:
            courses = self.get_courses_by_teacher(teacher)
            print(f"\n=== {teacher} 的课表 ===")
        else:
            print("\n=== 完整课表 ===")
            courses = list(self.courses.values())
        
        if not courses:
            print("暂无课程")
            return
        
        # 按时间排序
        courses.sort(key=lambda x: (x.day, x.period))
        
        for course in courses:
            print(f"{course.name} | 老师:{course.teacher} | 周{course.day} 第{course.period}-{course.period + course.duration - 1}节")
    
    def save_to_file(self, filename: str):
        """保存课表到文件"""
        data = {
            'courses': [course.to_dict() for course in self.courses.values()]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"课表已保存到 {filename}")
    
    def load_from_file(self, filename: str):
        """从文件加载课表"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.courses.clear()
            self.teacher_schedule.clear()
            
            for course_data in data.get('courses', []):
                course = Course.from_dict(course_data)
                self.add_course(course)
            
            print(f"课表已从 {filename} 加载")
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
        except json.JSONDecodeError:
            print(f"文件 {filename} 格式错误")


def main():
    """主函数"""
    manager = ScheduleManager()
    
    print("=" * 50)
    print("教务系统调课软件")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 添加课程")
        print("2. 显示课表")
        print("3. 调课")
        print("4. 删除课程")
        print("5. 保存课表")
        print("6. 加载课表")
        print("7. 查看老师课表")
        print("0. 退出")
        
        choice = input("请输入选项 (0-7): ").strip()
        
        if choice == '0':
            print("感谢使用，再见!")
            break
        
        elif choice == '1':
            # 添加课程
            course_id = input("课程ID: ").strip()
            name = input("课程名称: ").strip()
            teacher = input("老师姓名: ").strip()
            day = int(input("星期几 (1-7): "))
            period = int(input("开始节次 (1-12): "))
            duration = int(input("持续节次 (默认1): ") or "1")
            
            course = Course(course_id, name, teacher, day, period, duration)
            
            has_conflict, conflicts = manager.check_conflict(course)
            if has_conflict:
                print("\n⚠️ 添加失败，存在冲突:")
                for conflict in conflicts:
                    print(f"  - {conflict}")
                continue
            
            if manager.add_course(course):
                print("✅ 课程添加成功!")
            else:
                print("❌ 课程添加失败!")
        
        elif choice == '2':
            # 显示课表
            day_input = input("查看哪天的课表? (1-7, 留空查看全部): ").strip()
            if day_input:
                manager.display_schedule(day=int(day_input))
            else:
                manager.display_schedule()
        
        elif choice == '3':
            # 调课
            course_id = input("要调整的课程ID: ").strip()
            if course_id not in manager.courses:
                print("❌ 课程不存在!")
                continue
            
            course = manager.courses[course_id]
            print(f"当前课程: {course.name} | 周{course.day} 第{course.period}-{course.period + course.duration - 1}节")
            
            print("\n选择调整方式:")
            print("1. 调整星期")
            print("2. 调整节次")
            print("3. 同时调整星期和节次")
            
            mod_choice = input("请选择 (1-3): ").strip()
            
            new_day = None
            new_period = None
            
            if mod_choice in ['1', '3']:
                new_day = int(input("新的星期几 (1-7): "))
            
            if mod_choice in ['2', '3']:
                new_period = int(input("新的开始节次 (1-12): "))
            
            success, message = manager.modify_course(course_id, new_day, new_period)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        elif choice == '4':
            # 删除课程
            course_id = input("要删除的课程ID: ").strip()
            if manager.remove_course(course_id):
                print("✅ 课程删除成功!")
            else:
                print("❌ 课程不存在或删除失败!")
        
        elif choice == '5':
            # 保存课表
            filename = input("保存文件名 (默认schedule.json): ").strip() or "schedule.json"
            manager.save_to_file(filename)
        
        elif choice == '6':
            # 加载课表
            filename = input("加载文件名 (默认schedule.json): ").strip() or "schedule.json"
            manager.load_from_file(filename)
        
        elif choice == '7':
            # 查看老师课表
            teacher = input("老师姓名: ").strip()
            manager.display_schedule(teacher=teacher)
        
        else:
            print("❌ 无效选项，请重新选择!")


if __name__ == "__main__":
    main()