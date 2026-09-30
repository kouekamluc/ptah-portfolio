import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import (
    SiteSettings,
    TechnologyCategory,
    Technology,
    CurrentlyBuilding,
    TimelineItem,
    Education,
    SocialLink,
    Organization,
)
from projects.models import (
    ProjectCategory,
    Project,
    ProjectMetric,
)
from notes.models import (
    NoteCategory,
    Note,
)


class Command(BaseCommand):
    help = "Seeds database with Ptah Kouekam's engineering and software portfolio structure and initial data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding portfolio data..."))

        # 1. Site Settings (Singleton)
        site_settings, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                "full_name": "Ptah Kouekam Kamgou Luc Kevin",
                "professional_title": "Engineer. Developer. Builder.",
                "short_bio": (
                    "Engineering student studying Mechatronics Engineering / Engineering Science in Italy. "
                    "Building practical systems across physical mechanics, embedded electronics, and robust web software."
                ),
                "long_bio": (
                    "I am an engineering student studying Mechatronics Engineering and Engineering Science in Italy. "
                    "My work is grounded in first principles: understanding physical phenomena, modeling mechanical and "
                    "electrical systems, building prototypes, measuring real-world responses, and engineering software that connects them.\n\n"
                    "Rather than confining myself to a single narrow title, I approach engineering as an integrated discipline. "
                    "From discrete analogue circuits, sensor acquisition, and microcontrollers (Arduino, ESP32) to production Django web "
                    "applications, automated tooling, and computational simulations, I focus on building reliable, verifiable systems."
                ),
                "location": "Italy",
                "public_email": "contact@ptahkouekam.engineering",
                "availability_status": "collab",
                "resume_version": "2026.1",
                "footer_text": "Engineered with precision using Django, HTMX, and Tailwind CSS. Built to evolve.",
                "seo_meta_keywords": (
                    "Ptah Kouekam Kamgou Luc Kevin, Mechatronics Engineering, Engineering Science Italy, "
                    "Embedded Systems, Django Developer, Electronics, Control Systems, Arduino, ESP32, Python"
                ),
            }
        )
        if not created:
            site_settings.full_name = "Ptah Kouekam Kamgou Luc Kevin"
            site_settings.professional_title = "Engineer. Developer. Builder."
            site_settings.short_bio = (
                "Engineering student studying Mechatronics Engineering / Engineering Science in Italy. "
                "Building practical systems across physical mechanics, embedded electronics, and robust web software."
            )
            site_settings.long_bio = (
                "I am an engineering student studying Mechatronics Engineering and Engineering Science in Italy. "
                "My work is grounded in first principles: understanding physical phenomena, modeling mechanical and "
                "electrical systems, building prototypes, measuring real-world responses, and engineering software that connects them.\n\n"
                "Rather than confining myself to a single narrow title, I approach engineering as an integrated discipline. "
                "From discrete analogue circuits, sensor acquisition, and microcontrollers (Arduino, ESP32) to production Django web "
                "applications, automated tooling, and computational simulations, I focus on building reliable, verifiable systems."
            )
            site_settings.location = "Italy"
            site_settings.save()
        self.stdout.write(self.style.SUCCESS("[OK] Site Settings established."))

        # 2. Technology Categories & Concrete Technologies
        categories_data = [
            {
                "name": "Software & Web Systems",
                "display_order": 1,
                "technologies": [
                    {"name": "Python", "proficiency": "strong", "highlighted": True, "description": "Core language for backend systems, scripting, numeric modeling, and data pipelines."},
                    {"name": "Django", "proficiency": "strong", "highlighted": True, "description": "Server-rendered web architectures, robust ORM, authentication, and secure workflows."},
                    {"name": "PostgreSQL", "proficiency": "comfortable", "highlighted": True, "description": "Relational data modeling, schema normalization, ACID transactions, and query optimization."},
                    {"name": "HTMX", "proficiency": "strong", "highlighted": True, "description": "Progressive enhancement for reactive user interfaces without heavy client-side frameworks."},
                    {"name": "Tailwind CSS", "proficiency": "strong", "highlighted": True, "description": "Utility-first design systems, responsive interfaces, and dark/light theme systems."},
                    {"name": "Git & GitHub", "proficiency": "strong", "highlighted": True, "description": "Version control, branching strategies, and collaborative code reviews."},
                    {"name": "Linux / Bash", "proficiency": "comfortable", "highlighted": False, "description": "Server administration, development environments, and deployment automation."},
                ]
            },
            {
                "name": "Embedded Systems & Hardware",
                "display_order": 2,
                "technologies": [
                    {"name": "Arduino Ecosystem", "proficiency": "strong", "highlighted": True, "description": "Microcontroller firmware, hardware timer interrupts, and sensor interfacing."},
                    {"name": "ESP32", "proficiency": "comfortable", "highlighted": True, "description": "Dual-core 32-bit MCU, WiFi/BLE telemetry streaming, and FreeRTOS task partition."},
                    {"name": "C / C++", "proficiency": "comfortable", "highlighted": True, "description": "Embedded firmware development, register-level hardware control, and memory safety."},
                    {"name": "Sensors & Transducers", "proficiency": "comfortable", "highlighted": True, "description": "IMU, photogates, load cells, ultrasonic, temperature, and optical encoders."},
                    {"name": "Communication Protocols", "proficiency": "comfortable", "highlighted": False, "description": "UART, I2C, SPI, CAN bus fundamentals, and asynchronous data streaming."},
                    {"name": "Data Acquisition (DAQ)", "proficiency": "comfortable", "highlighted": False, "description": "Analogue-to-digital conversion, calibration, and noise mitigation."},
                ]
            },
            {
                "name": "Electronics & Instrumentation",
                "display_order": 3,
                "technologies": [
                    {"name": "Analogue Electronics", "proficiency": "working", "highlighted": True, "description": "Operational amplifiers, active filter stages, transistor biasing, and impedance matching."},
                    {"name": "Digital Electronics", "proficiency": "working", "highlighted": True, "description": "Logic gates, flip-flops, multiplexers, timing diagrams, and discrete digital blocks."},
                    {"name": "Circuit Analysis", "proficiency": "comfortable", "highlighted": False, "description": "Kirchhoff's laws, Thevenin/Norton equivalents, and frequency-domain response."},
                    {"name": "Oscilloscope & Multimeter", "proficiency": "comfortable", "highlighted": False, "description": "Laboratory signal measurement, transient analysis, and hardware debugging."},
                ]
            },
            {
                "name": "Control Systems & Mechanics",
                "display_order": 4,
                "technologies": [
                    {"name": "Control Systems", "proficiency": "working", "highlighted": True, "description": "Feedback loops, discrete PID tuning, stability criteria, and transfer functions."},
                    {"name": "Mechanics & Dynamics", "proficiency": "working", "highlighted": True, "description": "Newtonian mechanics, kinematics, torque, linkage systems, and friction compensation."},
                    {"name": "Machine Design", "proficiency": "working", "highlighted": False, "description": "Mechanical tolerances, structural sizing, stress considerations, and actuator selection."},
                    {"name": "CAD / 3D Modeling", "proficiency": "working", "highlighted": False, "description": "Mechanical component modeling, assembly drawings, and prototype fabrication."},
                ]
            },
            {
                "name": "Mathematics & Applied Physics",
                "display_order": 5,
                "technologies": [
                    {"name": "Calculus & Analysis", "proficiency": "comfortable", "highlighted": False, "description": "Multivariable calculus, vector fields, and series approximations for physical models."},
                    {"name": "Differential Equations", "proficiency": "comfortable", "highlighted": False, "description": "Ordinary differential equations governing mechanical and electrical physical systems."},
                    {"name": "Linear Algebra", "proficiency": "comfortable", "highlighted": False, "description": "Matrix operations, eigenvalues/eigenvectors, and state-space representations."},
                    {"name": "Applied Physics", "proficiency": "comfortable", "highlighted": False, "description": "Electromagnetism, classical mechanics, thermodynamics, and conservation laws."},
                ]
            },
            {
                "name": "Tools & Digital Media",
                "display_order": 6,
                "technologies": [
                    {"name": "DaVinci Resolve", "proficiency": "comfortable", "highlighted": True, "description": "Technical video editing, color grading, and documentary media post-production."},
                    {"name": "VS Code & Tooling", "proficiency": "strong", "highlighted": False, "description": "Configured developer environment with linters, language servers, and Git integration."},
                ]
            },
        ]

        tech_map = {}
        for cat_data in categories_data:
            cat, _ = TechnologyCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={"display_order": cat_data["display_order"]}
            )
            for t in cat_data["technologies"]:
                tech_obj, _ = Technology.objects.update_or_create(
                    name=t["name"],
                    defaults={
                        "category": cat,
                        "proficiency": t["proficiency"],
                        "highlighted": t["highlighted"],
                        "description": t["description"],
                    }
                )
                tech_map[t["name"]] = tech_obj
        self.stdout.write(self.style.SUCCESS("[OK] Technology stack categories and concrete items populated."))

        # 3. Education (Accurate: in-progress bachelor's in Italy)
        Education.objects.update_or_create(
            degree="Bachelor of Science in Mechatronics Engineering / Engineering Science",
            institution="University in Italy",
            defaults={
                "location": "Italy",
                "start_date": datetime.date(2023, 10, 1),
                "is_current": True,
                "description": (
                    "Rigorous interdisciplinary undergraduate engineering program integrating mechanical engineering, "
                    "electrical and electronics engineering, control systems, and computational methods. "
                    "Focuses on mathematical modeling of physical systems, laboratory measurement, and automation."
                ),
                "coursework": (
                    "Analogue and Digital Electronics; Automatic Control; Classical Control Theory; "
                    "Mechanics and Machine Design; Applied Physics; Mathematical Analysis & Linear Algebra; "
                    "Computer Science & Algorithms; Electrical Measurement & Instrumentation"
                ),
                "research_areas": (
                    "Sensor-actuator integration, closed-loop feedback controllers, embedded real-time systems, "
                    "and software platforms for engineering data telemetry."
                ),
                "display_order": 1,
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Academic education history recorded."))

        # 4. Currently Building (Active workbench items with clear stages & next milestones)
        CurrentlyBuilding.objects.all().delete()
        building_items = [
            {
                "title": "Projectile Launch Rig: Motorized Elevation & DAQ Upgrade",
                "description": "Fabricating a motorized servo-driven elevation base and high-speed photogate DAQ board for automated trajectory sweeps.",
                "status": "Mechanical Rig Fabricated & Testing Servos",
                "progress": 65,
                "category": "Mechatronics & Dynamics",
                "display_order": 1,
            },
            {
                "title": "ESP32 Dual-Core Sensor Telemetry Rig",
                "description": "Benchmarking FreeRTOS task partition across dual cores to stream multi-channel sensor packets over WiFi and UART.",
                "status": "Breadboard Firmware Validated",
                "progress": 75,
                "category": "Embedded Systems",
                "display_order": 2,
            },
            {
                "title": "Django Personal Finance & Ledger Tracker",
                "description": "Implementing double-entry accounting models and sub-50ms windowed query aggregations for monthly cash flow analytics.",
                "status": "Core Ledger & Models Implemented",
                "progress": 80,
                "category": "Software Architecture",
                "display_order": 3,
            },
        ]
        for b in building_items:
            CurrentlyBuilding.objects.create(**b)
        self.stdout.write(self.style.SUCCESS("[OK] Currently Building section updated with active milestones."))

        # 5. Social Links (Safe placeholders editable in admin)
        SocialLink.objects.all().delete()
        socials_data = [
            {"platform": "github", "display_name": "GitHub", "url": "https://github.com/kouekamluc", "username": "@kouekamluc", "show_in_hero": True, "show_in_nav": True, "show_in_footer": True, "display_order": 1},
            {"platform": "linkedin", "display_name": "LinkedIn", "url": "https://linkedin.com/in/YOUR_USERNAME", "username": "Ptah Kouekam", "show_in_hero": True, "show_in_nav": True, "show_in_footer": True, "display_order": 2},
            {"platform": "youtube", "display_name": "YouTube", "url": "https://youtube.com/@YOUR_CHANNEL", "username": "@YOUR_CHANNEL", "show_in_hero": False, "show_in_nav": False, "show_in_footer": True, "display_order": 3},
            {"platform": "x", "display_name": "X / Twitter", "url": "https://x.com/YOUR_HANDLE", "username": "@YOUR_HANDLE", "show_in_hero": False, "show_in_nav": False, "show_in_footer": True, "display_order": 4},
        ]
        for s in socials_data:
            SocialLink.objects.create(**s)
        self.stdout.write(self.style.SUCCESS("[OK] Configurable social links seeded."))

        # 6. Timeline Items
        TimelineItem.objects.all().delete()
        timeline_data = [
            {
                "title": "Mechatronics Engineering & Engineering Science Studies",
                "organization": "University in Italy",
                "location": "Italy",
                "start_date": datetime.date(2023, 10, 1),
                "is_current": True,
                "item_type": "education",
                "description": "Undergraduate engineering studies covering mechanical dynamics, electronic circuits, physics, mathematics, and control theory.",
                "display_order": 1,
            },
            {
                "title": "Independent Systems & Software Development",
                "organization": "Personal Engineering Lab",
                "location": "Italy",
                "start_date": datetime.date(2022, 1, 1),
                "is_current": True,
                "item_type": "experience",
                "description": "Continuous development of embedded prototypes, sensor DAQ pipelines, Django web systems, and technical documentation.",
                "display_order": 2,
            },
            {
                "title": "Hardware/Software Integration Milestones",
                "organization": "Laboratory & Prototyping Projects",
                "location": "Italy",
                "start_date": datetime.date(2024, 3, 1),
                "is_current": True,
                "item_type": "milestone",
                "description": "Validated closed-loop microcontroller feedback systems, multi-sensor telemetries, and automated testing tools.",
                "display_order": 3,
            }
        ]
        for t in timeline_data:
            TimelineItem.objects.create(**t)
        self.stdout.write(self.style.SUCCESS("[OK] Timeline milestones recorded."))

        # 7. Project Categories
        pcat_mechatronics, _ = ProjectCategory.objects.get_or_create(name="Mechatronics & Robotics", defaults={"display_order": 1})
        pcat_software, _ = ProjectCategory.objects.get_or_create(name="Software & Web Architecture", defaults={"display_order": 2})
        pcat_embedded, _ = ProjectCategory.objects.get_or_create(name="Embedded & IoT Systems", defaults={"display_order": 3})
        pcat_electronics, _ = ProjectCategory.objects.get_or_create(name="Analogue & Digital Electronics", defaults={"display_order": 4})
        pcat_control, _ = ProjectCategory.objects.get_or_create(name="Control Systems & Modeling", defaults={"display_order": 5})

        # =========================================================================
        # PROJECTS SEEDING (Curated Breadth: 1 Eng, 1 Software, 1 Embedded, 1 Civic)
        # =========================================================================

        # Project 1 (FEATURED #1 - Engineering): Projectile-Motion Dynamics Prototype
        p1, _ = Project.objects.update_or_create(
            title="Projectile-Motion Dynamics Simulation & Experimental Ballistics Prototype",
            defaults={
                "tagline": "Computational trajectory modeling incorporating aerodynamic drag, angle optimization, and sensor-verified launch mechanics.",
                "project_type": "mechatronics",
                "category": pcat_mechatronics,
                "status": "prototype",
                "start_date": datetime.date(2024, 2, 1),
                "is_featured": True,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/projectile-motion-dynamics",
                "overview": (
                    "An experimental engineering project investigating Newtonian mechanics and kinematics. "
                    "Combines a Python numerical simulation modeling non-linear atmospheric drag against a fabricated physical "
                    "spring-actuated projectile launch testbench fitted with optical photogates for velocity verification."
                ),
                "problem": (
                    "Introductory physics models assume a parabolic trajectory in a vacuum ($m \\ddot{y} = -mg$). "
                    "In physical air, quadratic velocity drag ($F_d = \\frac{1}{2} \\rho v^2 C_d A$) creates non-linear differential equations that cannot be solved analytically."
                ),
                "objectives": (
                    "1. Solve non-linear trajectory differential equations numerically via 4th-order Runge-Kutta (RK4).\n"
                    "2. Measure initial exit velocity accurately using infrared photogate timing.\n"
                    "3. Correlate measured impact distance with computational predictions within a +/- 5% error margin."
                ),
                "system_architecture": (
                    "Hardware: Mechanical launch apparatus with angular degree vernier, dual infrared beam photogates connected to Arduino high-speed timer interrupt.\n"
                    "Software: Python simulation script computing trajectory curves, optimal launch angles, and plotting comparisons against measured trial data."
                ),
                "hardware_specs": (
                    "- Optical Timing: Dual IR photogates spaced 50 mm apart\n"
                    "- Timer Precision: Arduino hardware Timer1 running with 0.5 microsecond clock resolution\n"
                    "- Mechanical Rig: Variable angle elevation base (0 - 90 degrees) with calibrated compression spring"
                ),
                "software_stack_details": (
                    "- Firmware: C++ with direct register manipulation and input capture interrupt service routines\n"
                    "- Numerical Solver: Python using NumPy / SciPy RK4 integrator\n"
                    "- Data Plotting: Matplotlib trajectory superposition against experimental impact marks"
                ),
                "engineering_process": (
                    "Phase 1: Mathematical formulation of 2D quadratic drag equations in Cartesian coordinates.\n"
                    "Phase 2: Fabrication of the launch tube, vernier elevation pivot, and spring release trigger.\n"
                    "Phase 3: Breadboard integration of dual infrared photogates and comparator threshold calibration.\n"
                    "Phase 4: Writing Arduino ISR timer code and conducting repeated exit velocity calibrations.\n"
                    "Phase 5: Field ballistic testing across launch angles from 15 to 75 degrees and recording impact ranges."
                ),
                "challenges": (
                    "Microsecond-scale timer jitter and optical sensor alignment. Solved by tuning comparator thresholds "
                    "and utilizing microcontroller hardware timer input capture interrupts rather than software polling."
                ),
                "solution": (
                    "Configured dedicated hardware input capture interrupts on ATmega2560 Timer1, yielding sub-microsecond timing accuracy "
                    "independent of main loop execution speed."
                ),
                "quantitative_results": (
                    "Empirical initial muzzle velocity measured at 4.82 m/s (+/- 0.04 m/s). Measured physical range matched "
                    "RK4 numerical drag predictions within 3.8% across 20 test firings."
                ),
                "lessons_learned": (
                    "Optical sensor alignment and high timer clock resolution are critical for microsecond-level velocity measurement. "
                    "Aerodynamic drag effects become noticeable even at moderate projectile velocities."
                ),
                "future_improvements": (
                    "Incorporate a motorized servo-driven elevation base to automate angle adjustments based on simulated target coordinates."
                ),
                "display_order": 1,
            }
        )
        if "Mechanics & Dynamics" in tech_map:
            p1.technologies.set([tech_map["Mechanics & Dynamics"], tech_map["Applied Physics"], tech_map["Calculus & Analysis"], tech_map["Arduino Ecosystem"], tech_map["Python"]])
        ProjectMetric.objects.filter(project=p1).delete()
        ProjectMetric.objects.create(project=p1, label="Timer Resolution", value="0.5 us", description="Arduino Timer1 interrupt")
        ProjectMetric.objects.create(project=p1, label="Model Correlation", value="96.2%", description="RK4 drag simulation vs measured impact")
        ProjectMetric.objects.create(project=p1, label="Exit Velocity", value="4.82 m/s", description="IR photogate verified")

        # Project 2 (FEATURED #2 - Software): Django Personal Finance Tracker
        p2, _ = Project.objects.update_or_create(
            title="Django Personal Finance & Cash Flow Tracker",
            defaults={
                "tagline": "Full-stack personal finance platform for cash flow tracking, expense categorization, financial forecasting, and report generation.",
                "project_type": "software",
                "category": pcat_software,
                "status": "in_development",
                "start_date": datetime.date(2024, 3, 1),
                "is_featured": True,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/django-personal-finance",
                "overview": (
                    "A secure, normalized Django web application engineered to give individuals precise visibility into their personal finances. "
                    "Supports multi-account transaction ledgers, recurring payment tracking, dynamic category budgets, and analytical visual breakdowns."
                ),
                "problem": (
                    "Commercial finance apps frequently require intrusive bank-linking, compromise privacy, or lock personal financial data behind subscription paywalls."
                ),
                "objectives": (
                    "1. Deliver double-entry bookkeeping accuracy with zero balance discrepancy across accounts.\n"
                    "2. Enable instant transaction categorization and monthly budget alerts.\n"
                    "3. Provide clean CSV/PDF export capability for personal accounting and tax records."
                ),
                "system_architecture": (
                    "Built with standard Django MVT architecture. Features custom Django ORM managers for running balance computations, "
                    "atomic database transactions to guarantee ledger consistency, and HTMX for inline transaction creation without full page reloads."
                ),
                "software_stack_details": (
                    "- Backend: Python, Django, PostgreSQL / SQLite\n"
                    "- Frontend: Django Templates, Tailwind CSS, HTMX\n"
                    "- Security: CSRF tokens, strict user isolation via query filtering, session-based authentication"
                ),
                "engineering_process": (
                    "Phase 1: Relational schema design for accounts, transaction splits, and categories.\n"
                    "Phase 2: Implementing atomic transaction handlers to prevent ledger drift.\n"
                    "Phase 3: Building HTMX dynamic forms for zero-reload ledger entry.\n"
                    "Phase 4: Constructing monthly cash flow analytics views using windowed database aggregations."
                ),
                "challenges": (
                    "Handling historical running balance computations across thousands of transactions without causing query latency. "
                    "Addressed using database-level window functions (`OVER (ORDER BY date)`) in Django ORM expressions."
                ),
                "solution": (
                    "Optimized database indexing on `(user_id, date)` and leveraged database aggregate expressions to ensure sub-50ms report generation."
                ),
                "quantitative_results": (
                    "Enforces double-entry ledger balancing with zero reconciliation discrepancy; sub-50ms report generation across multi-thousand transaction tables."
                ),
                "lessons_learned": (
                    "Relational integrity and ACID transactions are essential for financial software: always enforce constraints at the database level."
                ),
                "future_improvements": (
                    "Implement automated recurring transaction scheduler using Celery and add multi-currency exchange rate conversion."
                ),
                "display_order": 2,
            }
        )
        if "Django" in tech_map:
            p2.technologies.set([tech_map["Django"], tech_map["Python"], tech_map["PostgreSQL"], tech_map["Tailwind CSS"], tech_map["HTMX"]])
        ProjectMetric.objects.filter(project=p2).delete()
        ProjectMetric.objects.create(project=p2, label="Architecture", value="Django MVT", description="Relational double-entry ledger")
        ProjectMetric.objects.create(project=p2, label="Data Integrity", value="ACID Verified", description="Atomic transaction blocks")
        ProjectMetric.objects.create(project=p2, label="Query Latency", value="< 50 ms", description="Indexed windowed aggregates")

        # Project 3 (FEATURED #3 - Embedded): Multi-Sensor Telemetry & Embedded Acquisition
        p3, _ = Project.objects.update_or_create(
            title="Multi-Sensor Telemetry & Embedded Acquisition System",
            defaults={
                "tagline": "Real-time multi-channel sensor data acquisition, digital filtering, and telemetry streaming via ESP32 and FreeRTOS.",
                "project_type": "embedded",
                "category": pcat_embedded,
                "status": "prototype",
                "start_date": datetime.date(2024, 2, 10),
                "is_featured": True,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/esp32-multisensor-telemetry",
                "overview": (
                    "An embedded engineering platform engineered to acquire high-frequency data from multiple analogue and digital sensors, "
                    "apply on-chip digital filtering (moving average and IIR), and stream synchronized telemetry packets over serial and WiFi."
                ),
                "problem": (
                    "Sensor readings in physical prototypes frequently suffer from high-frequency electromagnetic interference, supply noise, "
                    "and non-deterministic sampling jitter when processed sequentially without real-time task scheduling."
                ),
                "objectives": (
                    "1. Guarantee a deterministic sampling loop of 1 kHz across all connected channels.\n"
                    "2. Partition sampling and communication tasks across dual cores using FreeRTOS.\n"
                    "3. Stream low-latency telemetry packets with zero packet drop over continuous multi-hour test cycles."
                ),
                "system_architecture": (
                    "The system utilizes an ESP32 dual-core microcontroller running FreeRTOS. Core 0 is dedicated to high-priority ADC sampling "
                    "and hardware interrupts, while Core 1 handles digital filtering algorithms, packet serialization, and communications."
                ),
                "hardware_specs": (
                    "- Controller: ESP32-WROOM-32 (240 MHz dual-core, 520 KB SRAM)\n"
                    "- Peripheral Bus: SPI for external 16-bit ADC (ADS1115), I2C for 6-DoF IMU (MPU6050)\n"
                    "- Power Supply: LDO regulated 3.3V with decoupling ceramic/tantalum capacitor network\n"
                    "- Isolation: Active opamp buffer stage for input impedance isolation"
                ),
                "software_stack_details": (
                    "- Firmware: C++ / ESP-IDF with FreeRTOS multitasking\n"
                    "- Buffer Queue: Thread-safe FreeRTOS ring buffers\n"
                    "- Host Interface: Python data parsing script with real-time matplotlib/numpy plotting"
                ),
                "engineering_process": (
                    "Phase 1: Mathematical modeling of sensor transfer characteristics and expected noise spectrum.\n"
                    "Phase 2: Breadboard verification of analogue anti-aliasing passive RC filters.\n"
                    "Phase 3: FreeRTOS task partition and priority benchmarking using hardware logic analyzer pins.\n"
                    "Phase 4: Calibration against laboratory bench power supply and precision multimeter."
                ),
                "challenges": (
                    "Encountered ADC cross-talk when sampling high-impedance sensor outputs simultaneously. Resolved by introducing "
                    "a unity-gain operational amplifier buffer stage prior to ADC conversion pins."
                ),
                "solution": (
                    "Integrated an active dual-opamp impedance buffer and configured differential ADC sampling mode to eliminate common-mode ground noise."
                ),
                "quantitative_results": (
                    "Achieved 1.002 kHz continuous sampling frequency with less than 0.8% variance. Signal-to-noise ratio improved by 18 dB "
                    "following analogue filtering and on-chip digital moving average windowing."
                ),
                "lessons_learned": (
                    "Hardware signal integrity is paramount: software digital filtering cannot compensate for severe analogue aliasing. "
                    "Designing proper input impedance matching simplifies downstream processing immensely."
                ),
                "future_improvements": (
                    "Design custom 2-layer surface-mount PCB in KiCAD and implement onboard microSD logging in addition to wireless telemetry."
                ),
                "display_order": 3,
            }
        )
        if "ESP32" in tech_map:
            p3.technologies.set([tech_map["ESP32"], tech_map["C / C++"], tech_map["Sensors & Transducers"], tech_map["Python"]])
        ProjectMetric.objects.filter(project=p3).delete()
        ProjectMetric.objects.create(project=p3, label="Sampling Rate", value="1.0 kHz", description="Deterministic FreeRTOS loop")
        ProjectMetric.objects.create(project=p3, label="ADC Resolution", value="16-bit", description="External ADS1115 over I2C")
        ProjectMetric.objects.create(project=p3, label="Transmission Latency", value="< 2.4 ms", description="Packet buffer to host")

        # Project 4 (FEATURED #4 - Civic Tech): Django Citizen Incident Management System
        p4, _ = Project.objects.update_or_create(
            title="Django Citizen Incident & Complaint Management System",
            defaults={
                "tagline": "Independent civic reporting and incident routing platform with status tracking pipelines and administrative dashboards.",
                "project_type": "software",
                "category": pcat_software,
                "status": "prototype",
                "start_date": datetime.date(2024, 5, 1),
                "is_featured": True,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/citizen-complaint-system",
                "overview": (
                    "An independent civic technology exploration designed to examine transparent communication pipelines between citizens "
                    "and municipal service departments. Enables public filing of community issues (infrastructure, sanitation, lighting), "
                    "automated departmental routing, and real-time status tracking via unique reference keys. (Note: Independent software prototype; not an official government deployment)."
                ),
                "problem": (
                    "Traditional municipal grievance reporting is opaque, fragmented across paper forms or obscure hotlines, "
                    "and provides citizens with zero visibility into whether reported public-works problems are scheduled, triaged, or resolved."
                ),
                "objectives": (
                    "1. Provide a clean public portal for citizens to submit verified reports with geo-coordinates and photo evidence.\n"
                    "2. Implement role-based administrative dashboards for municipal department staff to triage and update incident statuses.\n"
                    "3. Issue unique cryptographic tracking tokens allowing citizens to check real-time resolution status without account registration."
                ),
                "system_architecture": (
                    "Role-based access control (Citizens, Department Reviewers, Super-Admins). Utilizes custom Django signals for automated notifications "
                    "upon state transitions (Submitted -> Under Review -> Action Scheduled -> Resolved)."
                ),
                "software_stack_details": (
                    "- Backend: Django, Python, SQLite / PostgreSQL\n"
                    "- Frontend: Semantic HTML5, Tailwind CSS\n"
                    "- Features: Media upload validation, unique tracking tokens, role-based view decorators, honeypot protection"
                ),
                "engineering_process": (
                    "Phase 1: Departmental workflow mapping and state-transition diagramming.\n"
                    "Phase 2: Database normalization for incident categories, geo-coordinates, and attachments.\n"
                    "Phase 3: Public submission portal with client-side image compression and anti-spam validation.\n"
                    "Phase 4: Admin triage dashboard with status transition triggers and staff audit logs."
                ),
                "challenges": (
                    "Preventing spam reports while maintaining low friction for public anonymous filings. Addressed with honeypot fields and IP-based submission limits."
                ),
                "solution": (
                    "Separated the citizen reporting flow from the authenticated staff administration portal, keeping the public interface lightweight and accessible."
                ),
                "quantitative_results": (
                    "Enforces 4-stage incident lifecycle state machine; zero auth friction for public filings with cryptographically random 12-char tracking tokens."
                ),
                "lessons_learned": (
                    "Clear state machine modeling is vital when designing workflow platforms involving multiple human approval stages."
                ),
                "future_improvements": (
                    "Integrate interactive Leaflet.js mapping for cluster visualization of civic incidents across municipal districts."
                ),
                "display_order": 4,
            }
        )
        if "Django" in tech_map:
            p4.technologies.set([tech_map["Django"], tech_map["Python"], tech_map["Tailwind CSS"], tech_map["PostgreSQL"]])
        ProjectMetric.objects.filter(project=p4).delete()
        ProjectMetric.objects.create(project=p4, label="Workflow", value="4-Stage State Machine", description="Triage to resolution")
        ProjectMetric.objects.create(project=p4, label="Protection", value="Honeypot + Throttling", description="Spam and bot mitigation")
        ProjectMetric.objects.create(project=p4, label="Tracking Key", value="12-char Token", description="No account registration required")

        # Project 5 (Archive): ASCAI.org Community Platform
        p5, _ = Project.objects.update_or_create(
            title="ASCAI.org Student Community Platform & Association Hub",
            defaults={
                "tagline": "Community web platform and student directory built to help Cameroonian students navigating life in the Lazio region of Italy.",
                "project_type": "software",
                "category": pcat_software,
                "status": "archived",
                "start_date": datetime.date(2023, 9, 1),
                "end_date": datetime.date(2024, 9, 1),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/ascai-community-platform",
                "overview": (
                    "A volunteer community contribution developed to support Cameroonian students navigating academic enrollment, "
                    "housing, administrative procedures, and community integration across universities in the Lazio region of Italy. "
                    "Centralized community guides, association announcements, and peer networking resources. (Currently archived/offline "
                    "following student association leadership rotation and recurring hosting lifecycle decisions)."
                ),
                "problem": (
                    "International students arriving in Italy face fragmented documentation, complex regional bureaucratic procedures, "
                    "and a lack of centralized student community announcements."
                ),
                "objectives": (
                    "1. Provide a reliable, centralized resource directory for students.\n"
                    "2. Streamline announcements and community event coordination.\n"
                    "3. Maintain low operational costs suited for a non-profit student association."
                ),
                "system_architecture": (
                    "Django web architecture with admin-curated announcements, document download portal, and responsive Tailwind styling."
                ),
                "software_stack_details": (
                    "- Backend: Python, Django, PostgreSQL\n"
                    "- Styling: Responsive Tailwind CSS\n"
                    "- Delivery: Linux VPS deployment with WhiteNoise static handling"
                ),
                "lessons_learned": (
                    "Community software engineering is as much about long-term organizational ownership and recurring hosting budgets "
                    "as it is about technical code. Handover procedures must be planned early."
                ),
                "display_order": 5,
            }
        )
        if "Django" in tech_map:
            p5.technologies.set([tech_map["Django"], tech_map["Python"], tech_map["Tailwind CSS"]])

        # Project 6 (Archive): KKEVO Tech Initiative
        p6, _ = Project.objects.update_or_create(
            title="KKEVO Tech Platform & Engineering Initiative",
            defaults={
                "tagline": "Global technology and engineering initiative developing integrated hardware, embedded tools, and web software systems.",
                "project_type": "other",
                "category": pcat_software,
                "status": "in_development",
                "start_date": datetime.date(2024, 1, 1),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/kkevo-tech",
                "overview": (
                    "An independent global technology project serving as an umbrella initiative for hardware prototyping, "
                    "embedded tooling, and web software systems. Focused on modular engineering architecture, developer utilities, "
                    "and experimental physical computing."
                ),
                "objectives": (
                    "1. Develop modular, open-architecture engineering tools and hardware interfaces.\n"
                    "2. Create high-reliability software applications and automation pipelines.\n"
                    "3. Build scalable technical products grounded in engineering first principles."
                ),
                "system_architecture": (
                    "Modular software services and hardware schematics engineered for interoperability and extensible deployment."
                ),
                "display_order": 6,
            }
        )

        # Project 7 (Archive): KKEVO Studio Media
        p7, _ = Project.objects.update_or_create(
            title="KKEVO Studio Media Initiative",
            defaults={
                "tagline": "Independent digital media project exploring geopolitics, history, sovereignty, and African world affairs. Tagline: Facts. Perspective. Impact.",
                "project_type": "other",
                "category": pcat_software,
                "status": "maintained",
                "start_date": datetime.date(2024, 1, 1),
                "is_featured": False,
                "is_published": True,
                "overview": (
                    "An editorial and digital media project focused on rigorous analysis of international relations, history, "
                    "geopolitics, societal developments, and African world affairs (including Sahel/AES regional dynamics). "
                    "Operating under the editorial tagline 'Facts. Perspective. Impact.', the initiative documents complex "
                    "historical and contemporary phenomena through video essays and written analyses."
                ),
                "objectives": (
                    "1. Deliver disciplined, fact-based analysis of geopolitical and historical events.\n"
                    "2. Provide clear perspective on sovereignty, regional integration, and global affairs.\n"
                    "3. Produce high-standard documentary and technical media content using DaVinci Resolve."
                ),
                "software_stack_details": (
                    "- Production: DaVinci Resolve for video editing and audio mastering\n"
                    "- Editorial: Research documentation, historical archives, and scriptwriting pipelines"
                ),
                "display_order": 7,
            }
        )

        # Project 8 (Archive): Closed-Loop Inverted Pendulum
        p8, _ = Project.objects.update_or_create(
            title="Closed-Loop Inverted Pendulum / Balancing System",
            defaults={
                "tagline": "Dynamic stabilization and feedback control of an inverted pendulum system utilizing tuned PID algorithms and complementary filtering.",
                "project_type": "control",
                "category": pcat_control,
                "status": "testing",
                "start_date": datetime.date(2024, 4, 1),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/closed-loop-balancing-pid",
                "overview": (
                    "An experimental mechatronic system investigating classical feedback control theory. "
                    "The system dynamically computes vehicle tilt angle using an accelerometer/gyroscope sensor fusion algorithm "
                    "and drives dual DC motors via an H-bridge driver to maintain upright equilibrium."
                ),
                "problem": (
                    "An inverted pendulum is inherently unstable with an open-loop pole in the right-half s-plane. "
                    "Sensor noise, actuator backlash, and deadband non-linearities destabilize simple linear feedback."
                ),
                "objectives": (
                    "1. Attain stable limit-cycle equilibrium within +/- 1.5 degrees of vertical.\n"
                    "2. Recover from manual pulse disturbance forces up to 1.2 N.\n"
                    "3. Model the system differential equations and compare simulated response with measured physical dynamics."
                ),
                "hardware_specs": (
                    "- Microcontroller: Arduino / ATmega328P with high-resolution hardware timers\n"
                    "- Sensors: MPU-6050 (3-axis gyroscope + 3-axis accelerometer)\n"
                    "- Actuators: Dual 12V metal gearmotors with optical quadrature encoders\n"
                    "- Driver: MOSFET Dual H-Bridge module with 20 kHz PWM"
                ),
                "quantitative_results": (
                    "System recovers from 15-degree initial displacement within 1.1 seconds with less than 8% overshoot."
                ),
                "display_order": 8,
            }
        )
        if "Control Systems" in tech_map:
            p8.technologies.set([tech_map["Control Systems"], tech_map["Arduino Ecosystem"], tech_map["C / C++"]])

        # Project 9 (Archive): Precision Analogue Signal Conditioning
        p9, _ = Project.objects.update_or_create(
            title="Precision Analogue Signal Conditioning & Active Filter Stage",
            defaults={
                "tagline": "Design and experimental verification of low-noise instrumentation amplifiers and Sallen-Key active filters for micro-signal extraction.",
                "project_type": "electronics",
                "category": pcat_electronics,
                "status": "prototype",
                "start_date": datetime.date(2024, 6, 1),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/analogue-signal-conditioning",
                "overview": (
                    "An experimental electronics project focusing on conditioning weak analogue signals from high-impedance resistive bridge sensors. "
                    "Features a three-op-amp instrumentation amplifier topology followed by a 2nd-order active low-pass Butterworth filter."
                ),
                "hardware_specs": (
                    "- Active Components: Precision Operational Amplifiers (TL072 / OP07)\n"
                    "- Passive Components: 1% metal-film precision resistors and low-leakage film capacitors\n"
                    "- Circuit Topology: Three-op-amp instrumentation front-end, Sallen-Key low-pass filter"
                ),
                "quantitative_results": (
                    "Measured CMRR of 88.4 dB at 50 Hz. Cutoff frequency measured at 148 Hz (-3 dB point) with -40 dB/decade attenuation."
                ),
                "display_order": 9,
            }
        )
        if "Analogue Electronics" in tech_map:
            p9.technologies.set([tech_map["Analogue Electronics"], tech_map["Circuit Analysis"]])

        # Project 10 (Archive): Django Timetable & Academic Workload Planner
        p10, _ = Project.objects.update_or_create(
            title="Django Timetable & Academic Workload Planner",
            defaults={
                "tagline": "University course timetable planner with lecture scheduling, conflict detection, and academic milestone tracking.",
                "project_type": "software",
                "category": pcat_software,
                "status": "concept",
                "start_date": datetime.date(2024, 7, 1),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/academic-timetable-planner",
                "overview": (
                    "A specialized academic scheduling tool developed to help engineering students manage lecture timings, "
                    "laboratory sessions, coursework deadlines, and exam preparation countdowns in one unified interface."
                ),
                "display_order": 10,
            }
        )
        if "Django" in tech_map:
            p10.technologies.set([tech_map["Django"], tech_map["Python"], tech_map["Tailwind CSS"]])

        # Project 11 (Archive): Production Django Engineering Identity Platform
        p11, _ = Project.objects.update_or_create(
            title="Production Django Engineering Identity & Portfolio Platform",
            defaults={
                "tagline": "Modern, lightweight, server-rendered digital identity platform built with Django, HTMX, Tailwind CSS, and zero bloated JavaScript.",
                "project_type": "software",
                "category": pcat_software,
                "status": "completed",
                "start_date": datetime.date(2024, 8, 15),
                "is_featured": False,
                "is_published": True,
                "github_url": "https://github.com/YOUR_USERNAME/ptah-engineering-portfolio",
                "overview": (
                    "The personal digital architecture powering this website. Designed as a flexible, multi-discipline showcase "
                    "for mechatronics engineering, software systems, electronics notes, and professional milestones."
                ),
                "display_order": 11,
            }
        )
        if "Django" in tech_map:
            p11.technologies.set([tech_map["Django"], tech_map["Python"], tech_map["HTMX"], tech_map["Tailwind CSS"], tech_map["PostgreSQL"]])

        # 8. Seed Organizations & Initiatives
        Organization.objects.all().delete()
        Organization.objects.create(
            name="ASCAI.org",
            role="Co-Founder / Technical Contributor",
            description="Student association platform supporting Cameroonian students in the Lazio region of Italy with academic guidance, resource directories, and community integration.",
            website="https://ascai.org",
            period="2023 - 2024",
            is_active=False,
            display_order=1,
        )
        Organization.objects.create(
            name="KKEVO Tech",
            role="Founder & Technical Lead",
            description="Global technology and engineering initiative developing integrated hardware, embedded tools, and web software systems.",
            website="https://github.com/YOUR_USERNAME",
            period="2024 - Present",
            is_active=True,
            display_order=2,
        )
        Organization.objects.create(
            name="KKEVO Studio Media",
            role="Editorial Director",
            description="Independent digital media project exploring geopolitics, history, sovereignty, and African world affairs under the tagline: 'Facts. Perspective. Impact.'",
            website="https://youtube.com/@YOUR_CHANNEL",
            period="2024 - Present",
            is_active=True,
            display_order=3,
        )
        self.stdout.write(self.style.SUCCESS("[OK] Organizations and initiatives recorded."))

        # 9. Note Categories & Technical Notes
        ncat_engineering, _ = NoteCategory.objects.get_or_create(name="Engineering & Electronics", defaults={"display_order": 1})
        ncat_software, _ = NoteCategory.objects.get_or_create(name="Software Architecture", defaults={"display_order": 2})
        ncat_control, _ = NoteCategory.objects.get_or_create(name="Control Theory & Dynamics", defaults={"display_order": 3})

        Note.objects.update_or_create(
            title="Understanding Closed-Loop PID Tuning: From Equations to Real Microcontrollers",
            defaults={
                "category": ncat_control,
                "tags": "Control Systems, PID, Arduino, Mechatronics, Feedback",
                "is_published": True,
                "is_featured": True,
                "excerpt": (
                    "A practical engineering guide bridging the gap between mathematical transfer functions in the s-domain "
                    "and discrete difference equations implemented inside real-time microcontroller loops."
                ),
                "content_markdown": """## 1. Introduction

In textbook control theory, the Proportional-Integral-Derivative (PID) controller is frequently expressed in continuous time:

$$u(t) = K_p e(t) + K_i \\int_0^t e(\\tau) d\\tau + K_d \\frac{de(t)}{dt}$$

Where:
- $e(t) = r(t) - y(t)$ is the tracking error between desired reference and measured output
- $K_p$ is proportional gain
- $K_i$ is integral gain (eliminating steady-state error)
- $K_d$ is derivative gain (damping rate of change)

When deploying this on an Arduino, ESP32, or STM32, we cannot calculate continuous integrals or derivatives. We must translate the system into the discrete time domain.

---

## 2. Discrete Approximation (Euler Backward Difference)

For a fixed sampling interval $\\Delta t$:

$$\\int_0^t e(\\tau)d\\tau \\approx \\sum_{k=1}^N e[k] \\Delta t$$

$$\\frac{de(t)}{dt} \\approx \\frac{e[k] - e[k-1]}{\\Delta t}$$

This yields the canonical discrete position-form PID equation:

```cpp
float error = setpoint - measured_value;
integral_sum += error * dt;
float derivative = (error - previous_error) / dt;

float output = (Kp * error) + (Ki * integral_sum) + (Kd * derivative);
previous_error = error;
```

---

## 3. Practical Realities: Derivative Kick & Windup

In physical systems, two severe issues emerge if implemented naively:

### A. Derivative Kick
When the setpoint changes abruptly, $de/dt$ produces an infinite or massive spike because the setpoint jumps instantaneously. 
**Solution**: Compute derivative on measurement instead of error:

$$\\frac{d}{dt}(-y(t)) = -\\frac{y[k] - y[k-1]}{\\Delta t}$$

### B. Integral Windup
If the actuator saturates (e.g. PWM hits 100%), the integral term keeps accumulating error. When the system finally reaches the setpoint, it severely overshoots while the integral unwinds.
**Solution**: Clamp the integral accumulation or freeze integration whenever the output hits maximum limits.

---

## 4. Key Takeaways
1. Always run PID loops at a strictly deterministic sampling rate (using hardware timer interrupts or RTOS delays).
2. Filter the derivative term with a low-pass filter to prevent high-frequency sensor noise from chattering the actuator.
3. Anti-windup clamping is non-negotiable for real physical systems.
""",
            }
        )

        Note.objects.update_or_create(
            title="Designing Resilient Server-Rendered Web Apps with Django and HTMX",
            defaults={
                "category": ncat_software,
                "tags": "Django, HTMX, Architecture, Performance, Python",
                "is_published": True,
                "is_featured": True,
                "excerpt": (
                    "Why modern web engineering does not always require multi-megabyte JavaScript frameworks, and how Django plus HTMX "
                    "delivers maximum speed, reliability, and maintainability."
                ),
                "content_markdown": """## The Problem with Excessive Client-Side Complexity

Over the past decade, frontend web development drifted toward massive Single Page Applications (SPAs). While SPAs have valid use cases for high-density tools like CAD editors or spreadsheet apps, using them for content, portfolios, and standard web products introduces immense overhead:

- Duplicate state management across client and server
- Fragmented authentication and complex CORS configurations
- Large JavaScript bundles that impair mobile performance and battery life
- Hydration mismatch bugs and fragile build pipelines

---

## The Progressive Enhancement Philosophy

With **Django and HTMX**, the server remains the single source of truth:

1. **Semantic HTML First**: The server renders standard, accessible HTML that works even if JavaScript is disabled.
2. **Selective Interactivity**: HTMX attributes (`hx-get`, `hx-target`, `hx-swap`) progressively intercept links and forms to swap only the necessary DOM fragments.
3. **No Build Step Hell**: HTML is processed with standard Django templates, keeping developer iteration rapid and enjoyable.

---

## Real-World Example: Dynamic Project Filtering

```html
<div hx-get="/projects/" 
     hx-target="#project-grid" 
     hx-push-url="true" 
     hx-indicator="#loading-spinner">
    <!-- Server returns only the #project-grid partial on HTMX requests -->
</div>
```

The Django view cleanly inspects `request.headers.get("HX-Request")`:
- If `True`, render just `partials/project_grid.html`.
- If `False`, render the complete `projects/list.html` with headers, navigation, and footers.

Fast, maintainable, and built to last.
""",
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Engineering notes and technical articles seeded."))

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Database seeding completed successfully!"))
