import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import User, Pet, Task, Walk, Scheduler

# Page configuration
st.set_page_config(page_title="PawPal+", layout="wide")

st.title("🐾 PawPal+ - Pet Care Scheduler")

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
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Add Pet", "Schedule Walk", "Today's Tasks"])

# Home Page
if page == "Home":
    st.header(f"Welcome, {user.name}!")
    st.write(f"📧 Email: {user.email}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pets", len(user.pets))
    with col2:
        st.metric("Today's Tasks", len(user.getTodaysTasks()))
    with col3:
        st.metric("Scheduled Walks", len(user.walks))
    
    st.subheader("Your Pets")
    if user.pets:
        for pet in user.pets:
            st.write(f"🐶 {pet.getDetails()}")
    else:
        st.info("No pets added yet. Go to 'Add Pet' to get started!")

# Add Pet Page
elif page == "Add Pet":
    st.header("Add a New Pet")
    
    with st.form("add_pet_form"):
        pet_name = st.text_input("Pet Name")
        pet_breed = st.text_input("Breed")
        pet_age = st.number_input("Age", min_value=0, max_value=30, step=1)
        
        submitted = st.form_submit_button("Add Pet")
        
        if submitted and pet_name and pet_breed:
            new_pet = Pet(
                petId=f"pet_{len(user.pets) + 1}",
                name=pet_name,
                breed=pet_breed,
                age=pet_age
            )
            user.addPet(new_pet)
            st.success(f"✅ {pet_name} added successfully!")
        elif submitted:
            st.error("Please fill in all fields.")

# Schedule Walk Page
elif page == "Schedule Walk":
    st.header("Schedule a Walk")
    
    if not user.pets:
        st.warning("No pets available. Please add a pet first.")
    else:
        pet_name = st.selectbox("Select Pet", [pet.name for pet in user.pets])
        selected_pet = next(pet for pet in user.pets if pet.name == pet_name)
        
        walk_date = st.date_input("Walk Date")
        walk_time = st.time_input("Walk Time")
        duration = st.number_input("Duration (minutes)", min_value=5, max_value=120, step=5)
        
        if st.button("Schedule Walk"):
            walk_datetime = datetime.combine(walk_date, walk_time)
            scheduler.scheduleWalk(selected_pet, walk_datetime, duration)
            st.success(f"✅ Walk scheduled for {pet_name} on {walk_date} at {walk_time}")

# Today's Tasks Page
elif page == "Today's Tasks":
    st.header("Today's Schedule")
    
    organized_tasks = scheduler.getOrganizedTodaysTasks()
    
    if not organized_tasks:
        st.info("No tasks scheduled for today.")
    else:
        for pet_name, tasks in organized_tasks.items():
            with st.expander(f"🐾 {pet_name}", expanded=True):
                for task in sorted(tasks, key=lambda t: t.dueDate):
                    col1, col2, col3 = st.columns([0.5, 3, 1])
                    
                    with col1:
                        # Use a unique key and callback to handle checkbox changes
                        is_checked = st.checkbox(
                            "Done", 
                            value=task.isCompleted, 
                            key=task.taskId,
                            label_visibility="collapsed"
                        )
                        if is_checked and not task.isCompleted:
                            next_task = scheduler.completeTask(task)
                            if next_task:
                                st.success(f"✅ Task completed! Next occurrence scheduled for {next_task.dueDate.strftime('%m/%d')}")
                            st.rerun()
                    
                    with col2:
                        time_str = task.dueDate.strftime("%I:%M %p")
                        priority_icon = "🔴" if task.priority == "high" else "🟡"
                        recurrence_badge = f" 🔄 {task.recurrence.capitalize()}" if task.recurrence else ""
                        status_style = "✓ ~~" if task.isCompleted else ""
                        st.write(f"{status_style}{time_str} - {task.description} {priority_icon}{recurrence_badge}")
                    
                    with col3:
                        st.write(f"Status: {'✓' if task.isCompleted else '○'}")
