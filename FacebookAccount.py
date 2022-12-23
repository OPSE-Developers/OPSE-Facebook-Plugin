#!/usr/bin/python3
# -*- coding: utf-8 -*-
from classes.account.Account import Account


class FacebookAccount(Account):
    """
    Class which define a FacebookAccount in OPSE context
    """

    def __init__(
        self,
        username: str,
        url: str,
        image_url: str
    ):
        """Constructor of an OPSE FacebookAccount"""
        super().__init__(username, url)
        self.__image_url: str = image_url

    def get_image_url(self) -> str:
        """Getter of self.__image_url"""
        return self.__image_url
