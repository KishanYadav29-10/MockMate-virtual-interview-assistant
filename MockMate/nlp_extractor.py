import re

SKILL_DB = [
    "python", "java", "c++", "machine learning", "deep learning", "nlp",
    "data analysis", "streamlit", "pandas", "numpy", "matplotlib", "seaborn",
    "sql", "mysql", "html", "css", "javascript", "django", "flask",
    "scikit-learn", "tensorflow", "pytorch", "keras", "opencv"
]

def extract_email(text):
    if not text or text.startswith("⚠️ No readable text"):
        return None
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None

def extract_phone(text):
    if not text or text.startswith("⚠️ No readable text"):
        return None
    match = re.search(r'(\+91[\s\-]*)?(\d{5}[\s\-]?\d{5})', text)
    return match.group(0).replace(" ", "").replace("-", "") if match else None


def extract_name(text):
    # First try to extract using known patterns
    name_match = re.search(r"(?:^|\n)([A-Z][a-z]+(?: [A-Z][a-z]+)+)", text)
    if name_match:
        return name_match.group(1).strip()

    # Fallback: Check first few lines for likely name
    lines = text.strip().split('\n')
    for line in lines[:10]:
        line = line.strip()
        if line and not any(char.isdigit() for char in line) and 2 <= len(line.split()) <= 4:
            return line
    return "Name Not Found"

def extract_skills(text):
    if not text or text.startswith("⚠️ No readable text"):
        return []
    text = text.lower()
    found_skills = [skill for skill in SKILL_DB if skill in text]
    return list(set(found_skills))

def extract_sections(text):
    sections = {}
    if not text or text.startswith("⚠️ No readable text"):
        return sections
    lines = text.split('\\n')
    current_section = None

    known_section_keywords = {
        'Experience': ['experience', 'work history', 'tools', 'libraries/frameworks'],
        'Projects': ['project', 'jobguard', 'ecovision', 'eda', 'stable diffusion', 'text-to-image'],
        'Education': ['education'],
        'Certifications': ['certification'],
        'Technical Skills': ['technical skills'],
        'Languages': ['languages'],
        'Soft Skills': ['soft skills'],
    }

    all_keywords = [kw for kws in known_section_keywords.values() for kw in kws]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower_line = line.lower()

        matched_section = None
        for section, keywords in known_section_keywords.items():
            if any(kw in lower_line for kw in keywords):
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            sections[current_section] = []
        elif current_section:
            if any(kw in lower_line for kw in all_keywords):
                current_section = None
            else:
                sections[current_section].append(line)

    return sections

def extract_projects(text):
    projects = []
    if not text or text.startswith("⚠️ No readable text"):
        return projects

    lines = text.split('\n')
    current_project = []
    capture = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if "|" in line and "GitHub" in line:
            if current_project:
                projects.append('\n'.join(current_project))
                current_project = []
            capture = True
            current_project.append(line)
        elif capture:
            if line.startswith("–") or line.startswith("-") or line.startswith("•"):
                current_project.append(line)
            else:
                if any(keyword in line.lower() for keyword in ["skills", "certifications", "education", "languages"]):
                    capture = False
                    if current_project:
                        projects.append('\n'.join(current_project))
                        current_project = []
                else:
                    current_project.append(line)

    if current_project:
        projects.append('\n'.join(current_project))

    return projects
