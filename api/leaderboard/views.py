from leaderboard.models import CodeforcesUser
from leaderboard.serializers import Cf_Serializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status

from datetime import datetime, timedelta
from random import randint, choice
import requests


class GithubUserAPI(APIView):
    """
    Collects Github data for registered users
    """

    REGISTERED_GH_USERS = [
        "KShivendu",
        "ArsphreetS",
        # Contributors may add their Github username here
    ]

    def _get_github_data(self, username: str, days_passed=7):
        """
        TODO
        """

        return {
            "username": username,
            "commits": randint(1, 100),
            "rank": randint(1, 100),
        }

    def get(self, request, format=None):
        gh_users = [
            self._get_github_data(gh_username)
            for gh_username in self.REGISTERED_GH_USERS
        ]
        gh_users.sort(key=lambda r: r.get("rank", 0))

        return Response(gh_users)


class GithubOrganisationAPI(APIView):
    """
    Collects Github data for GH_ORG
    """

    GH_ORG = "OpenLake"

    def _get_github_data(self, days_passed=7):
        """
        TODO:
        """

        repos = requests.get("https://api.github.com/users/OpenLake/repos").json()
        return [
            {
                "username": f"gh_user_{i}",
                "commits": randint(1, 100),
                "rank": randint(1, 100),
                "contributions": {choice(repos)["name"]: randint(1, 100)},
            }
            for i in range(10)
        ]

    def get(self, request, format=None):
        gh_users = self._get_github_data()
        gh_users.sort(key=lambda r: r.get("rank", 0))

        return Response(gh_users)


class CodeforcesLeaderboard(APIView):
    """
    Collects data from codeforces API
    """

    def _check_for_updates(self, cf_users):
        cf_outdated_users = []
        for cf_user in cf_users:
            if cf_user.is_outdated:
                cf_outdated_users.append(cf_user.username)

        cf_api_response = {}

        if len(cf_outdated_users) > 0:
            url = f"https://codeforces.com/api/user.info?handles={';'.join(cf_outdated_users)}"
            cf_api_response = requests.get(url).json()
            cf_api_response = cf_api_response["result"]

        outdated_counter = 0
        for i, cf_user in enumerate(cf_users):

            if cf_user.is_outdated:
                user_info = cf_api_response[outdated_counter]
                outdated_counter += 1

                # TODO: Use serialier for saving data from codeforces API
                cf_user.max_rating = user_info.get("max_rating", 0)
                cf_user.rating = user_info.get("rating", 0)
                cf_user.last_activity = user_info.get(
                    "lastOnlineTimeSeconds", datetime.max.timestamp()
                )
                cf_user.save()

    def get(self, request, *args, **kwargs):
        cf_users = CodeforcesUser.objects.all()
        self._check_for_updates(cf_users)
        serializer = Cf_Serializer(cf_users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Registers a new username in the list
        """
        username = request.data["username"]
        cf_user = CodeforcesUser(username=username)
        cf_user.save()

        return Response(Cf_Serializer(cf_user).data, status=status.HTTP_201_CREATED)


class CodeforcesUserAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = CodeforcesUser.objects.all()
    serializer_class = Cf_Serializer


class CodechefAPI(APIView):
    """
    TODO
    """

    def get(self, request, format=None):
        # TODO

        return Response("TODO")