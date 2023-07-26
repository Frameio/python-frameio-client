import json
import os
from pathlib import Path
from time import time

from dotenv import find_dotenv, load_dotenv
from frameioclient import FrameioClient


class AccountScraper:
    def __init__(self, token=None, minimal=False):
        self.token = token
        self.client = FrameioClient(self.token)

        self.minimal = minimal  # Only fetch 2x teams
        self.final_data = None  # Store final data

    def get_team_ids(self):
        account_id = self.client.me["account_id"]
        teams_info = self.client.teams.list(account_id=account_id)

        # Slice the list and only return the data from the first two teams
        if self.minimal == True:
            teams_info = teams_info[0:2]

        team_id_list = list()
        for team in teams_info:
            team_id_list.append(
                {
                    "id": team["id"],
                    "name": team["name"],
                    "projects": team["project_count"],
                    "members": team["member_count"],
                    "storage": team["storage"],
                    "storage_limit": team["storage_limit"],
                    "date_created": team["inserted_at"],
                }
            )

        return team_id_list

    def custom_get_members(self, team_id):
        team_members = self.client.teams.get_members(team_id=team_id)
        clean_team_members = list()

        for member in team_members:
            user_object = member["user"]
            id = user_object["id"]
            name = user_object["name"]
            email = user_object["email"]

            clean_team_members.append({"id": id, "name": name, "email": email})

        return clean_team_members

    def custom_get_project_members(self, project_name, project_id):
        print(
            "Adding team members for project: {}, ID: {}".format(
                project_name, project_id
            )
        )
        project_members = self.client.projects.get_collaborators(project_id=project_id)

        results = []

        for member in project_members:
            user_object = member["user"]
            id = user_object["id"]
            name = user_object["name"]
            email = user_object["email"]

            try:
                joined_via = user_object["joined_via"]
                if joined_via == "account_member":
                    role = "Collaborator"
                elif joined_via == "organic":
                    role = "Team Member"
                else:
                    role = None

            except KeyError:
                role = None

            results.append({"id": id, "name": name, "email": email, "role": role})

        return results

    def persist_state(self):
        path = Path('.').joinpath("account_state.json")
        with open(path.as_posix(), "w") as account_data:
            json.dump(self.final_data, account_data)

        return True

    @staticmethod
    def clean_data(data=None):
        for team in data:
            # Grab the list of team members so we can then remove them from project membership
            team_members_list = team["members"]
            team_member_ids = []
            for team_member in team_members_list:
                team_member_ids.append(team_member["id"])

            for project in team["projects"]:
                project_members_list = project["collaborators"]
                for count, project_member in enumerate(project_members_list):
                    if project_member["id"] in team_member_ids:
                        project_members_list.pop(count)
        return data

    def do_it_all(self):
        """
        1. Get all team ids
        2. Get members list for all teams
        3. Get all projects
        4. Get all collaborators on each project
        5. Exclude TEAM MEMBERS, and then you have a list of people who are just collaborators
        """

        teams_list = self.get_team_ids()

        team_member_list = []  # reset blank list
        for count, team in enumerate(teams_list, start=1):
            print("Team {}/{}".format(count, len(teams_list)))
            membership_info = self.custom_get_members(team["id"])  # get membership info
            team[
                "members"
            ] = membership_info  # add member info to the team before passing it to the list

            print(
                "Adding projects for team: {}, ID: {}".format(team["name"], team["id"])
            )
            project_info = []
            projects_list = self.client.teams.list_projects(team_id=team["id"])

            for count, project in enumerate(projects_list, start=1):
                print("Project {}/{}".format(count, len(projects_list)))

                # Add the project info
                project_info.append(
                    {
                        "id": project["id"],
                        "date_created": project["inserted_at"],
                        "name": project["name"],
                        "owner_id": project["owner_id"],
                        "root_asset_id": project["root_asset"]["id"],
                        "file_count": project["file_count"],
                        "folder_count": project["folder_count"],
                        "storage": project["storage"],
                        "collaborators": self.custom_get_project_members(
                            project["name"], project["id"]
                        ),
                    }
                )

                print("Appended project info...")

            # Inject project info into the main JSON
            team["projects"] = project_info
            team_member_list.append(team)

        # Clean data (remove team members from members list in projects)
        cleaned_data = self.clean_data(team_member_list)

        self.final_data = cleaned_data
        self.persist_state()

        return True


if __name__ == "__main__":
    dotenv_file = find_dotenv('.env', True, False)
    load_dotenv(dotenv_file)
    token = os.getenv("FRAMEIO_TOKEN")
    AccountScraper(token=token, minimal=True).do_it_all()
