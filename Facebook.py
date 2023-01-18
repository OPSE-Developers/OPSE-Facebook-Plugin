#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
from typing import Any, Dict, List
import requests

from .FacebookAccount import FacebookAccount
from classes.Profile import Profile
from tools.Tool import Tool

from utils.config.Config import Config
from utils.datatypes import DataTypeInput
from utils.datatypes import DataTypeOutput
from utils.stdout import print_debug, print_error, print_warning


class FacebookTool(Tool):
    """
    Class which describe a FacebookTool
    """
    deprecated = False

    def __init__(self):
        """The constructor of a FacebookTool"""
        super().__init__()

    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Function which return tool configuration as a dictionnary."""
        return {
            'active': True,
        }

    @staticmethod
    def get_lst_input_data_types() -> Dict[str, bool]:
        """
        Function which return the list of data types which can be use to run this Tool.
        It's will help to make decision to run Tool depending on current data.
        """
        return {
            DataTypeInput.FIRSTNAME: True,
            DataTypeInput.LASTNAME: True,
        }

    @staticmethod
    def get_lst_output_data_types() -> List[str]:
        """
        Function which return the list of data types which can be receive by using this Tool.
        It's will help to make decision to complete profile to get more information.
        """
        return [
            DataTypeOutput.ACCOUNT,
        ]

    def execute(self):

        firstname = str(self.get_default_profile().get_firstname())
        lastname = str(self.get_default_profile().get_lastname())

        facebook_results = self.list_accounts(firstname, lastname)

        # Create a profile for each facebook account found
        # because each account might be a different person
        for facebook_account in facebook_results:
            profile: Profile = self.get_default_profile().clone()
            account = FacebookAccount(facebook_account['fullname'], facebook_account['url'],
                                      facebook_account['image'])
            profile.set_lst_accounts([account])
            self.append_profile(profile)

    def list_accounts(self, firstname: str, lastname: str) -> list:
        """
        Function to list Facebook accounts matching firstname and lastname
        """
        """
        This code is inspired by: 
        https://github.com/lulz3xploit/LittleBrother/blob/master/core/facebookSearchTool.py
        """

        f1 = firstname + " " + lastname
        f2 = lastname + " " + firstname
        url = "https://www.facebook.com/public/{}%20{}".format(firstname, lastname)

        # Try to get the Facebook page with accounts matching Firstname Lastname
        try:
            r = requests.get(url=url)
            page = r.content.decode('utf-8')
            print_debug("Facebook request succeed with a " + str(r.status_code) + " status code.")
        except Exception as e:
            print_error("[FacebookTool:list_accounts] Request failed: " + str(e), True)
            return None

        # Search in the result page the HTML anchor with fullname, account url and image url
        re_accounts = re.findall(
            "<a title=\"[a-zA-ZÀ-ÿ0-9_ é , ]+\" class=\"_2ial\" aria-label=\"[a-zA-ZÀ-ÿ0-9_ é , ]+\" aria-hidden=\"true\" tabindex=\"-1\" role=\"presentation\" href=\"http[s]://[a-zA-Z0-9\.-]+[.]facebook.com/[a-z]+[.][a-z]+[.]?[0-9]*\"><img class=\"_1glk _6phc img\" src=\"http[s]?://[a-zA-Z0-9\.-]+[.][a-zA-Z]{2,4}/[\S]+[.]jpg[?][\S]+\" width=\"72\" height=\"72\" alt=\"[a-zA-ZÀ-ÿ0-9_ é , ]+\" /></a>",
            page)

        # Redirection to Facebook login page might appened with too many request
        # You have to wait a little
        if r.status_code == 200 and len(re_accounts) == 0:
            rejected = re.findall(
                "Vous devez vous connecter pour continuer.|You must log in to continue.|Debes iniciar sesión para continuar.|Melde dich an, um fortzufahren.",
                page)
            if len(rejected) > 0:
                print_warning(" Facebook listing accounts is unavailable due to many requests")
                return []

        # If there are matches
        if len(re_accounts) > 0:
            accounts = []
            for a in re_accounts:
                parts = a.split('="')

                # Split to get to good parts
                fullname = parts[1].split('"')[0]
                url = parts[7].split('"')[0]
                image = parts[9].split('"')[0]

                if Config.is_strict():
                    if f1.lower() == fullname.lower() or f2.lower() == fullname.lower():
                        accounts.append({
                            'fullname': fullname,
                            'url': url,
                            'image': image
                        })
                else:
                    accounts.append({
                        'fullname': fullname,
                        'url': url,
                        'image': image
                    })

        if Config.is_strict():
            print_debug("Strict mode activated. Only " + str(len(accounts)) + " account" + ("s" if len(accounts) > 1 else "") + " match.")
        else:
            print_debug("Found " + str(len(re_accounts)) + " match" + ("es" if len(re_accounts) > 1 else "") + " in source code.")

        return accounts or []
