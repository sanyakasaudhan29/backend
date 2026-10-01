import json
import os
import urllib.parse
import urllib.request


# ---------------------------------------------------------
# DEMO FALLBACK DATA
# ---------------------------------------------------------

OPPORTUNITIES = [
    {
        "title": "AI/ML Internship",
        "organization": "Tech Innovations",
        "type": "Internship",
        "skills": ["Python", "Machine Learning", "AI"],
        "interests": ["Artificial Intelligence", "Machine Learning"],
        "eligibility": "BTech students with Python and AI/ML knowledge",
        "remote": True,
        "url": "",
        "deadline": "",
        "source": "GigGenie Demo Data"
    },
    {
        "title": "Generative AI Hackathon",
        "organization": "AI Builders",
        "type": "Hackathon",
        "skills": ["Python", "AI", "Generative AI"],
        "interests": ["Generative AI", "Hackathons"],
        "eligibility": "Students interested in Generative AI",
        "remote": True,
        "url": "",
        "deadline": "",
        "source": "GigGenie Demo Data"
    },
    {
        "title": "Python Developer Internship",
        "organization": "Software Labs",
        "type": "Internship",
        "skills": ["Python", "Git", "APIs"],
        "interests": ["Software Development"],
        "eligibility": "Students with basic Python development skills",
        "remote": True,
        "url": "",
        "deadline": "",
        "source": "GigGenie Demo Data"
    },
    {
        "title": "Data Science Challenge",
        "organization": "Data Community",
        "type": "Competition",
        "skills": ["Python", "Data Science", "Machine Learning"],
        "interests": ["Data Science", "AI"],
        "eligibility": "Students and beginners in Data Science",
        "remote": True,
        "url": "",
        "deadline": "",
        "source": "GigGenie Demo Data"
    }
]


# ---------------------------------------------------------
# LIVE BRABBLE API
# ---------------------------------------------------------

BRABBLE_API_URL = "https://brabble.ai/api/listings"


def _normalise_live_listing(listing, profile):
    """
    Convert a Brabble listing into the data format
    GigGenie already understands.
    """

    title = listing.get("title", "Untitled Opportunity")
    organization = listing.get("organiser", "Unknown Organization")
    listing_type = listing.get("type", "Opportunity")

    eligibility_list = listing.get("eligibility", [])

    if isinstance(eligibility_list, list):
        eligibility = "; ".join(str(item) for item in eligibility_list)
    else:
        eligibility = str(eligibility_list)

    mode = str(listing.get("mode", "ONLINE")).upper()

    remote = mode == "ONLINE"

    deadline = listing.get("deadline", "")
    url = listing.get("url", "")

    full_text = (
        title
        + " "
        + organization
        + " "
        + listing_type
        + " "
        + eligibility
    ).lower()

    # Try to identify the user's skills that are relevant
    # to this opportunity.
    profile_skills = profile.get("skills", [])

    matched_skills = []

    for skill in profile_skills:
        if str(skill).lower() in full_text:
            matched_skills.append(skill)

    # Use common opportunity keywords as searchable skills.
    common_skills = [
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "React",
        "Node.js",
        "AI",
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Generative AI",
        "Data Science",
        "Data Analytics",
        "Git",
        "APIs",
        "SQL",
        "Cloud",
        "AWS",
        "Azure",
        "Cybersecurity",
        "Web Development",
        "App Development",
        "Blockchain",
        "IoT",
        "NLP",
        "Computer Vision"
    ]

    detected_skills = []

    for skill in common_skills:
        if skill.lower() in full_text:
            detected_skills.append(skill)

    final_skills = list(
        dict.fromkeys(matched_skills + detected_skills)
    )

    profile_interests = profile.get("interests", [])

    matched_interests = []

    for interest in profile_interests:
        if str(interest).lower() in full_text:
            matched_interests.append(interest)

    return {
        "title": title,
        "organization": organization,
        "type": listing_type,
        "skills": final_skills,
        "interests": matched_interests,
        "eligibility": eligibility
        if eligibility
        else "Check the official opportunity page for eligibility.",
        "remote": remote,
        "url": url,
        "deadline": deadline,
        "source": "Brabble",
        "platform": listing.get("platform", ""),
        "fee": listing.get("fee", ""),
        "prize": (
            listing.get("prize", {}).get("label", "")
            if isinstance(listing.get("prize"), dict)
            else ""
        ),
        "team": listing.get("team", ""),
        "city": listing.get("city", "")
    }


def search_live_opportunities(profile):
    """
    Try to retrieve current student opportunities from Brabble.

    If the API key is missing, invalid, or the network request
    fails, return an empty list so GigGenie can safely use
    the demo fallback data.
    """

    api_key = os.getenv("BRABBLE_API_KEY")

    if not api_key:
        return []

    try:
        params = {
            "hub": "college-students",
            "limit": "50"
        }

        url = (
            BRABBLE_API_URL
            + "?"
            + urllib.parse.urlencode(params)
        )

        request = urllib.request.Request(
            url,
           headers={
    "x-api-key": api_key,
    "Accept": "application/json"
} 
        )

        with urllib.request.urlopen(
            request,
            timeout=8
        ) as response:

            if response.status != 200:
                return []

            data = json.loads(
                response.read().decode("utf-8")
            )

        listings = data.get("listings", [])

        opportunities = []

        for listing in listings:

            normalized = _normalise_live_listing(
                listing,
                profile
            )

            opportunities.append(normalized)

        return opportunities

    except Exception:
        # Never let the external API break GigGenie.
        return []


# ---------------------------------------------------------
# MAIN OPPORTUNITY SEARCH
# ---------------------------------------------------------

def search_opportunities(profile=None):
    """
    GigGenie's opportunity-search tool.

    Priority:
    1. Live Brabble opportunities
    2. Existing demo opportunities

    This makes the application reliable even when the
    internet or API is unavailable.
    """

    if profile is None:
        profile = {}

    live_opportunities = search_live_opportunities(
        profile
    )

    if live_opportunities:
        return live_opportunities

    return OPPORTUNITIES


# ---------------------------------------------------------
# ELIGIBILITY CHECK
# ---------------------------------------------------------

def check_eligibility(profile, opportunity):
    """
    Check whether a student appears eligible for an
    opportunity based on available skill information.
    """

    skills = {
        str(skill).lower()
        for skill in profile.get("skills", [])
    }

    opportunity_skills = {
        str(skill).lower()
        for skill in opportunity.get("skills", [])
    }

    matched_skills = skills & opportunity_skills

    if matched_skills:
        return {
            "eligible": True,
            "matched_requirements": list(
                matched_skills
            ),
            "message": (
                "Profile satisfies relevant "
                "skill requirements."
            )
        }

    # Some opportunities have broad student eligibility.
    eligibility_text = str(
        opportunity.get("eligibility", "")
    ).lower()

    broad_student_terms = [
        "student",
        "college",
        "undergraduate",
        "btech",
        "university"
    ]

    if any(
        term in eligibility_text
        for term in broad_student_terms
    ):
        return {
            "eligible": True,
            "matched_requirements": [],
            "message": (
                "The opportunity appears open to "
                "students. Check the official listing "
                "before applying."
            )
        }

    return {
        "eligible": False,
        "matched_requirements": [],
        "message": (
            "Additional skills may be required "
            "before applying."
        )
    }