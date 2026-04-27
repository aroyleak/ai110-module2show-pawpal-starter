import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import User, Pet, Task, Walk, Scheduler

# Page configuration
st.set_page_config(page_title="PawPal+", layout="wide", initial_sidebar_state="expanded")

st.title("🐾 PawPal+ - Intelligent Pet Care Scheduler")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = User(
        userId="user_001",
        name="Malik",
        email="malik@pawpal.com"
    )
    st.session_state.scheduler = Scheduler(st.session_state.user)

user = st.session_state.user
scheduler = st.session_state.scheduler

# Sidebar navigation
st.sidebar.header("🗂️ Navigation")
page = st.sidebar.radio("Select a page:", [
    "Home",
    "Add Pet",
    "Schedule Walk",
    "Today's Tasks",
    "Analytics"
])

# ============================================================================
# HOME PAGE
# ============================================================================
if page == "Home":
    st.header(f"Welcome, {user.name}! 👋")
    st.write(f"📧 Email: {user.email}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🐕 Total Pets", len(user.pets))
    with col2:
        today_tasks = len(user.getTodaysTasks())
        st.metric("📋 Today's Tasks", today_tasks)
    with col3:
        pending = len(scheduler.getPendingTasks())
        st.metric("⏳ Pending", pending)
    with col4:
        completed = len(scheduler.getCompletedTasks())
        st.metric("✅ Completed", completed)
    
    st.divider()
    
    # Your Pets Section
    st.subheader("Your Pets")
    if user.pets:
        pet_cols = st.columns(len(user.pets))
        for idx, pet in enumerate(user.pets):
            with pet_cols[idx]:
                st.write(f"### {pet.name}")
                st.write(f"**Breed:** {pet.breed}")
                st.write(f"**Age:** {pet.age} years")
                pet_tasks = len([t for t in pet.tasks if not t.isCompleted])
                st.write(f"**Pending Tasks:** {pet_tasks}")
    else:
        st.info("🐾 No pets added yet. Go to 'Add Pet' to get started!")
    
    st.divider()
    
    # Quick Schedule Preview (Organized by Priority + Time)
    st.subheader("📅 Quick Schedule Preview")
    today_organized = scheduler.getOrganizedTodaysTasks()
    
    if today_organized:
        for pet_name, tasks in today_organized.items():
            with st.expander(f"🐾 {pet_name}", expanded=True):
                task_data = []
                for task in tasks:  # Already sorted by priority + time
                    status_icon = "✅" if task.isCompleted else "⏳"
                    priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                    recurrence_badge = f" [🔄 {task.recurrence.upper()}]" if task.recurrence else ""
                    
                    task_data.append({
                        "Status": status_icon,
                        "Time": task.dueDate.strftime("%I:%M %p"),
                        "Task": f"{task.description}{recurrence_badge}",
                        "Priority": priority_icon,
                    })
                
                st.dataframe(task_data, use_container_width=True, hide_index=True)
    else:
        st.info("✨ No tasks scheduled for today!")

# ============================================================================
# ADD PET PAGE
# ============================================================================
elif page == "Add Pet":
    st.header("🐾 Add a New Pet")
    
    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pet_name = st.text_input("Pet Name", placeholder="e.g., Buddy")
            pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        
        with col2:
            pet_breed = st.text_input("Breed", placeholder="e.g., Golden Retriever")
            pet_id = f"pet_{len(user.pets) + 1:03d}"
        
        submit = st.form_submit_button("✅ Add Pet", use_container_width=True)
        
        if submit:
            if pet_name and pet_breed:
                new_pet = Pet(
                    petId=pet_id,
                    name=pet_name,
                    breed=pet_breed,
                    age=pet_age
                )
                user.addPet(new_pet)
                st.success(f"🎉 {pet_name} has been added to your pet family!")
                st.rerun()
            else:
                st.error("❌ Please fill in all fields!")

# ============================================================================
# SCHEDULE WALK PAGE (WITH CONFLICT DETECTION)
# ============================================================================
elif page == "Schedule Walk":
    st.header("🚶 Schedule a Walk")
    
    if not user.pets:
        st.warning("⚠️ Please add a pet first before scheduling walks!")
    else:
        with st.form("schedule_walk_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Pet selection
                pet_names = [p.name for p in user.pets]
                selected_pet_name = st.selectbox("Select Pet", pet_names)
                selected_pet = next(p for p in user.pets if p.name == selected_pet_name)
                
                # Duration
                duration = st.slider("Walk Duration (minutes)", 10, 120, 30)
            
            with col2:
                # Date and time
                walk_date = st.date_input("Walk Date", value=datetime.now().date())
                walk_time = st.time_input("Walk Time", value=datetime.now().time())
            
            # Combine date and time
            walk_datetime = datetime.combine(walk_date, walk_time)
            
            submit = st.form_submit_button("📅 Schedule Walk", use_container_width=True)
            
            if submit:
                # CHECK FOR CONFLICTS BEFORE SCHEDULING
                has_conflict, conflict_message = scheduler.hasConflict(selected_pet, walk_datetime, duration)
                
                if has_conflict:
                    # ⚠️ DISPLAY CONFLICT WARNING PROMINENTLY
                    st.error("❌ **CONFLICT DETECTED!**")
                    st.warning(conflict_message)
                    st.info(
                        "💡 **Suggestion:** Try scheduling at a different time. "
                        "See 'Today's Tasks' to view all scheduled activities."
                    )
                else:
                    # ✅ SCHEDULE THE WALK
                    scheduled_walk = scheduler.scheduleWalk(selected_pet, walk_datetime, duration)
                    
                    if scheduled_walk:
                        st.success(
                            f"✅ **Walk Scheduled!**\n\n"
                            f"🐾 **Pet:** {selected_pet.name}\n"
                            f"⏰ **Time:** {walk_datetime.strftime('%I:%M %p')}\n"
                            f"⏱️ **Duration:** {duration} minutes\n"
                            f"📅 **Date:** {walk_date.strftime('%A, %B %d, %Y')}"
                        )
                        st.balloons()
                        st.rerun()

# ============================================================================
# TODAY'S TASKS PAGE (SORTED, FILTERED, ORGANIZED)
# ============================================================================
elif page == "Today's Tasks":
    st.header("📋 Today's Schedule")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    today_tasks = scheduler.user.getTodaysTasks()
    pending_count = len(scheduler.getPendingTasks())
    completed_count = len(scheduler.getCompletedTasks())
    
    with col1:
        st.metric("📋 Total Tasks Today", len(today_tasks))
    with col2:
        st.metric("⏳ Pending", pending_count, delta=f"-{completed_count}" if completed_count > 0 else None)
    with col3:
        st.metric("✅ Completed", completed_count)
    
    st.divider()
    
    # Check for conflicts in entire schedule
    all_conflicts = scheduler.checkAllConflicts()
    
    if all_conflicts:
        st.warning("⚠️ **SCHEDULE CONFLICTS DETECTED!**")
        for conflict in all_conflicts:
            st.error(conflict)
        st.info("Please resolve conflicts by rescheduling overlapping walks.")
    else:
        st.success("✅ No conflicts in your schedule!")
    
    st.divider()
    
    # Organized schedule by pet
    organized_tasks = scheduler.getOrganizedTodaysTasks()
    
    if not organized_tasks:
        st.info("✨ No tasks scheduled for today!")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            show_pending = st.checkbox("Show Pending Tasks", value=True)
        with col2:
            show_completed = st.checkbox("Show Completed Tasks", value=False)
        
        # Display tasks by pet
        for pet_name, tasks in organized_tasks.items():
            with st.expander(f"🐾 {pet_name.upper()}", expanded=True):
                
                # Filter tasks based on checkboxes
                filtered_tasks = tasks
                if show_pending and not show_completed:
                    filtered_tasks = [t for t in tasks if not t.isCompleted]
                elif show_completed and not show_pending:
                    filtered_tasks = [t for t in tasks if t.isCompleted]
                
                if not filtered_tasks:
                    st.write("No tasks to display.")
                else:
                    for task in filtered_tasks:
                        # Create task card
                        col1, col2, col3 = st.columns([0.5, 3, 1])
                        
                        with col1:
                            # Checkbox to mark complete
                            is_checked = st.checkbox(
                                "Done",
                                value=task.isCompleted,
                                key=task.taskId,
                                label_visibility="collapsed"
                            )
                            
                            # Handle task completion
                            if is_checked and not task.isCompleted:
                                next_task = scheduler.completeTask(task)
                                if next_task:
                                    st.success(
                                        f"✅ Task completed! Next occurrence scheduled for "
                                        f"{next_task.dueDate.strftime('%m/%d at %I:%M %p')}"
                                    )
                                else:
                                    st.success("✅ Task completed!")
                                st.rerun()
                        
                        with col2:
                            time_str = task.dueDate.strftime("%I:%M %p")
                            priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                            recurrence_badge = f" 🔄 {task.recurrence.capitalize()}" if task.recurrence else ""
                            status_style = "✓ " if task.isCompleted else ""
                            
                            # Display task with strikethrough if completed
                            if task.isCompleted:
                                st.markdown(f"~~{time_str} - {task.description}~~ {priority_icon}{recurrence_badge}")
                            else:
                                st.write(f"{time_str} - {task.description} {priority_icon}{recurrence_badge}")
                        
                        with col3:
                            status_text = "✅ Done" if task.isCompleted else "⏳ Pending"
                            st.caption(status_text)

# ============================================================================
# ANALYTICS PAGE (NEW: SHOWCASES FILTERING & ORGANIZATION)
# ============================================================================
elif page == "Analytics":
    st.header("📊 Schedule Analytics")
    
    st.subheader("Tasks by Status")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Pending Tasks")
        pending = scheduler.getPendingTasks()
        if pending:
            pending_data = []
            for task in scheduler.sortTasksByPriority(pending):
                pet_name = task.pet.name if task.pet else "N/A"
                priority_emoji = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
                pending_data.append({
                    "Pet": pet_name,
                    "Task": task.description,
                    "Time": task.dueDate.strftime("%I:%M %p"),
                    "Priority": priority_emoji,
                })
            st.dataframe(pending_data, use_container_width=True, hide_index=True)
        else:
            st.info("All tasks completed! 🎉")
    
    with col2:
        st.write("### Completed Tasks")
        completed = scheduler.getCompletedTasks()
        if completed:
            completed_data = []
            for task in completed:
                pet_name = task.pet.name if task.pet else "N/A"
                completed_data.append({
                    "Pet": pet_name,
                    "Task": task.description,
                    "Time": task.dueDate.strftime("%I:%M %p"),
                })
            st.dataframe(completed_data, use_container_width=True, hide_index=True)
        else:
            st.info("No completed tasks yet.")
    
    st.divider()
    
    st.subheader("Tasks by Pet")
    for pet in user.pets:
        with st.expander(f"📈 {pet.name}"):
            pet_tasks = scheduler.getTasksByPetName(pet.name)
            
            if pet_tasks:
                # Breakdown by status
                col1, col2 = st.columns(2)
                
                with col1:
                    pending_pet = len([t for t in pet_tasks if not t.isCompleted])
                    st.metric(f"{pet.name}'s Pending", pending_pet)
                
                with col2:
                    completed_pet = len([t for t in pet_tasks if t.isCompleted])
                    st.metric(f"{pet.name}'s Completed", completed_pet)
                
                # All tasks for this pet
                st.write("**All Tasks (sorted by priority + time):**")
                sorted_pet_tasks = scheduler.sortTasksByPriority(pet_tasks)
                
                task_table = []
                for task in sorted_pet_tasks:
                    status = "✅" if task.isCompleted else "⏳"
                    recurrence = task.recurrence.upper() if task.recurrence else "One-time"
                    task_table.append({
                        "Status": status,
                        "Time": task.dueDate.strftime("%I:%M %p"),
                        "Task": task.description,
                        "Priority": task.priority.capitalize(),
                        "Type": recurrence,
                    })
                
                st.dataframe(task_table, use_container_width=True, hide_index=True)
            else:
                st.info(f"No tasks scheduled for {pet.name} yet.")
    
    st.divider()
    
    st.subheader("Recurring Tasks Overview")
    recurring = [t for t in user.tasks if t.recurrence]
    
    if recurring:
        recurring_table = []
        for task in recurring:
            pet_name = task.pet.name if task.pet else "N/A"
            next_date = task.getNextOccurrence()
            next_date_str = next_date.strftime("%m/%d at %I:%M %p") if next_date else "N/A"
            
            recurring_table.append({
                "Pet": pet_name,
                "Task": task.description,
                "Frequency": task.recurrence.capitalize(),
                "Current Due": task.dueDate.strftime("%m/%d at %I:%M %p"),
                "Next Due": next_date_str,
                "Status": "✅" if task.isCompleted else "⏳",
            })
        
        st.dataframe(recurring_table, use_container_width=True, hide_index=True)
    else:
        st.info("No recurring tasks set up yet.")
