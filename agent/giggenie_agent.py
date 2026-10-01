from tools.opportunity_search import (
    search_opportunities,
    check_eligibility
)


class GigGenieAgent:

    def __init__(self):
        self.name = "GigGenie"

    def analyze_profile(self, profile):
        return {
            "agent": self.name,
            "profile_summary": {
                "skills": profile.get("skills", []),
                "interests": profile.get("interests", []),
                "goals": profile.get("goals", [])
            },
            "message": "Profile successfully analyzed."
        }

    def find_opportunities(self, profile):

        opportunities = search_opportunities(profile)

        user_skills = {
            skill.lower()
            for skill in profile.get("skills", [])
        }

        user_interests = {
            interest.lower()
            for interest in profile.get("interests", [])
        }

        user_goals = {
            goal.lower()
            for goal in profile.get("goals", [])
        }

        matches = []

        for opportunity in opportunities:

            eligibility = check_eligibility(
                profile,
                opportunity
            )

            opportunity_skills = {
                skill.lower()
                for skill in opportunity.get("skills", [])
            }

            opportunity_interests = {
                interest.lower()
                for interest in opportunity.get(
                    "interests", []
                )
            }

            skill_matches = (
                user_skills & opportunity_skills
            )

            interest_matches = (
                user_interests & opportunity_interests
            )

            opportunity_text = (
                opportunity.get("title", "")
                + " "
                + opportunity.get("type", "")
                + " "
                + opportunity.get("eligibility", "")
            ).lower()

            goal_matches = set()

            for goal in user_goals:

                for word in goal.split():

                    if (
                        len(word) > 2
                        and word in opportunity_text
                    ):
                        goal_matches.add(word)

            score = (
                len(skill_matches) * 3
                + len(interest_matches) * 2
                + len(goal_matches)
            )

            if score > 0:

                matches.append({
                    "title": opportunity.get(
                        "title",
                        "Untitled Opportunity"
                    ),
                    "organization": opportunity.get(
                        "organization",
                        "Unknown Organization"
                    ),
                    "type": opportunity.get(
                        "type",
                        "Opportunity"
                    ),
                    "match_score": score,
                    "matched_skills": list(
                        skill_matches
                    ),
                    "matched_interests": list(
                        interest_matches
                    ),
                    "matched_goals": list(
                        goal_matches
                    ),
                    "eligibility": opportunity.get(
                        "eligibility",
                        "Check official listing."
                    ),
                    "remote": opportunity.get(
                        "remote",
                        False
                    ),
                    "eligible": eligibility["eligible"],
                    "eligibility_message": (
                        eligibility["message"]
                    ),
                    "url": opportunity.get(
                        "url",
                        ""
                    ),
                    "deadline": opportunity.get(
                        "deadline",
                        ""
                    ),
                    "source": opportunity.get(
                        "source",
                        "GigGenie"
                    ),
                    "platform": opportunity.get(
                        "platform",
                        ""
                    ),
                    "reasoning": (
                        f"Matched "
                        f"{len(skill_matches)} "
                        f"skill(s), "
                        f"{len(interest_matches)} "
                        f"interest(s), and "
                        f"{len(goal_matches)} "
                        f"goal-related factor(s)."
                    )
                })

        matches.sort(
            key=lambda x: x["match_score"],
            reverse=True
        )

        return matches

    def create_action_plan(
        self,
        profile,
        opportunities
    ):

        user_skills = {
            skill.lower()
            for skill in profile.get("skills", [])
        }

        action_plan = []

        all_opportunities = search_opportunities(
            profile
        )

        for opportunity in opportunities[:3]:

            original = next(
                (
                    item
                    for item in all_opportunities
                    if item.get("title")
                    == opportunity.get("title")
                ),
                None
            )

            required_skills = set()

            if original:

                required_skills = {
                    skill.lower()
                    for skill in original.get(
                        "skills",
                        []
                    )
                }

            missing_skills = (
                required_skills - user_skills
            )

            steps = [
                (
                    "Review eligibility for "
                    + opportunity["title"]
                ),
                "Prepare or update your resume",
                (
                    "Build a small project related "
                    "to the opportunity"
                )
            ]

            if missing_skills:

                steps.insert(
                    1,
                    "Learn these missing skills: "
                    + ", ".join(
                        sorted(missing_skills)
                    )
                )

            action_plan.append({
                "opportunity": opportunity[
                    "title"
                ],
                "organization": opportunity[
                    "organization"
                ],
                "match_score": opportunity[
                    "match_score"
                ],
                "missing_skills": sorted(
                    missing_skills
                ),
                "recommended_steps": steps
            })

        return action_plan