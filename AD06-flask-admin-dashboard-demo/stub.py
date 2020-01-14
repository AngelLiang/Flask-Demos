def get_messages_summary():
    m = {
        "from": "John Smith",
        "receivedon": "Yesterday",
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eleifend...",
        "url": "#"
    }
    messages = list()
    for i in range(3):
        messages.append(m)
    return messages


def get_tasks():
    t1 = {"name": "Task 1", "completed": 40, "type": "success"}
    t2 = {"name": "Task 2", "completed": 20, "type": "info"}
    t3 = {"name": "Task 3", "completed": 60, "type": "warning"}
    t4 = {"name": "Task 4", "completed": 80, "type": "danger"}
    return [t1, t2, t3, t4]


def get_alerts():
    a1 = {"title": "New Comment", "time": 4, "type": "comment", "url": "#"}
    a2 = {"title": "3 New Followers", "time": 12, "type": "twitter", "url": "#"}
    a3 = {"title": "Message Sent", "time": 4, "type": "envelope", "url": "#"}
    a4 = {"title": "New Task", "time": 4, "type": "tasks", "url": "#"}
    a5 = {"title": "Server Rebooted", "time": 4, "type": "upload", "url": "#"}
    return [a1, a2, a3, a4, a5]
