import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# ── class data ────────────────────────────────────────────────────────────────
classes = {
    "Pet": {
        "attrs": ["petId: str", "name: str", "breed: str", "age: int"],
        "methods": ["getDetails()", "getScheduledWalks()"],
    },
    "Walk": {
        "attrs": ["walkId: str", "scheduledTime: datetime", "duration: int", "status: str"],
        "methods": ["scheduleWalk()", "cancelWalk()", "completeWalk()"],
    },
    "Task": {
        "attrs": ["taskId: str", "description: str", "dueDate: datetime",
                  "priority: str", "isCompleted: bool", "recurrence: str"],
        "methods": ["markComplete()", "getPriority()", "isForToday()", "getNextOccurrence()"],
    },
    "User": {
        "attrs": ["userId: str", "name: str", "email: str",
                  "pets: List[Pet]", "tasks: List[Task]", "walks: List[Walk]"],
        "methods": ["addPet()", "getPets()", "getTodaysTasks()"],
    },
    "Scheduler": {
        "attrs": ["user: User"],
        "methods": ["scheduleWalk()", "completeTask()", "createRecurringTask()",
                    "sortTasksByPriority()", "hasConflict()", "checkAllConflicts()",
                    "getTasksByPetName()", "getTasksByStatus()", "getPendingTasks()",
                    "getOrganizedTodaysTasks()"],
    },
}

# ── layout: (center_x, center_y) ─────────────────────────────────────────────
positions = {
    "User":      (3.5, 8.5),
    "Pet":       (1.0, 5.0),
    "Task":      (3.5, 5.0),
    "Walk":      (6.0, 5.0),
    "Scheduler": (3.5, 1.5),
}

BOX_W = 2.6
FONT_SIZE = 7
HEADER_COLOR = "#1a1a2e"
ATTR_COLOR   = "#f0f0f5"
METHOD_COLOR = "#e0e8ff"
LINE_H = 0.28


def box_height(cls_name):
    d = classes[cls_name]
    return LINE_H * (1 + len(d["attrs"]) + 1 + len(d["methods"]) + 0.4)


fig, ax = plt.subplots(figsize=(12, 11))
ax.set_xlim(0, 7)
ax.set_ylim(0, 11)
ax.axis("off")
fig.patch.set_facecolor("#f8f9fc")

box_rects = {}  # store (left, bottom, width, height) for arrow anchoring

# ── draw each class box ───────────────────────────────────────────────────────
for cls_name, (cx, cy) in positions.items():
    d = classes[cls_name]
    h = box_height(cls_name)
    left = cx - BOX_W / 2
    top  = cy + h / 2

    # shadow
    shadow = mpatches.FancyBboxPatch(
        (left + 0.05, top - h - 0.05), BOX_W, h,
        boxstyle="round,pad=0.04", linewidth=0,
        facecolor="#ccccdd", zorder=1
    )
    ax.add_patch(shadow)

    # main box
    box = mpatches.FancyBboxPatch(
        (left, top - h), BOX_W, h,
        boxstyle="round,pad=0.04", linewidth=1.2,
        edgecolor="#333355", facecolor=ATTR_COLOR, zorder=2
    )
    ax.add_patch(box)
    box_rects[cls_name] = (left, top - h, BOX_W, h)

    y = top

    # header
    header_h = LINE_H * 1.3
    hdr = mpatches.FancyBboxPatch(
        (left, y - header_h), BOX_W, header_h,
        boxstyle="round,pad=0.04", linewidth=0,
        facecolor=HEADER_COLOR, zorder=3
    )
    ax.add_patch(hdr)
    ax.text(cx, y - header_h / 2, f"«class»\n{cls_name}",
            ha="center", va="center", fontsize=FONT_SIZE + 1,
            fontweight="bold", color="white", zorder=4,
            linespacing=1.4)
    y -= header_h

    # attributes
    for attr in d["attrs"]:
        ax.text(left + 0.12, y - LINE_H / 2, f"  {attr}",
                ha="left", va="center", fontsize=FONT_SIZE,
                color="#222244", zorder=4, fontstyle="italic")
        y -= LINE_H

    # divider
    ax.plot([left + 0.08, left + BOX_W - 0.08], [y, y],
            color="#aaaacc", linewidth=0.8, zorder=4)

    # methods
    for mth in d["methods"]:
        ax.text(left + 0.12, y - LINE_H / 2, f"  {mth}",
                ha="left", va="center", fontsize=FONT_SIZE,
                color="#003366", zorder=4)
        y -= LINE_H


def anchor(cls_name, side="center"):
    l, b, w, h = box_rects[cls_name]
    cx = l + w / 2
    cy = b + h / 2
    if side == "top":    return cx, b + h
    if side == "bottom": return cx, b
    if side == "left":   return l, cy
    if side == "right":  return l + w, cy
    return cx, cy


# ── arrows ────────────────────────────────────────────────────────────────────
arrows = [
    # (from_class, from_side, to_class, to_side, label)
    ("User",      "left",   "Pet",       "top",    "1  has  *"),
    ("User",      "bottom", "Task",      "top",    "1  has  *"),
    ("User",      "right",  "Walk",      "top",    "1  has  *"),
    ("Task",      "left",   "Pet",       "right",  "for"),
    ("Task",      "right",  "Walk",      "left",   "linked to"),
    ("Walk",      "bottom", "Pet",       "right",  ""),
    ("Scheduler", "top",    "User",      "bottom", "manages"),
]

for (src, ss, dst, ds, lbl) in arrows:
    x0, y0 = anchor(src, ss)
    x1, y1 = anchor(dst, ds)
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color="#333366",
                    lw=1.4,
                    connectionstyle="arc3,rad=0.08"
                ), zorder=5)
    if lbl:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my, lbl, ha="center", va="center",
                fontsize=6, color="#444466",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="#f8f9fc",
                          edgecolor="none", alpha=0.85),
                zorder=6)

ax.set_title("PawPal+ — UML Class Diagram", fontsize=14,
             fontweight="bold", color="#1a1a2e", pad=12)

plt.tight_layout()
plt.savefig("uml_final.png", dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved uml_final.png")
