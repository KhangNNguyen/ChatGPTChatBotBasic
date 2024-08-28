import discord
import datetime
import re

class Member:
    all = []
    
    def __init__(self, id, name, avatar, join_date, profile_color, linkedin="",  bio="") -> None:
        
        self._id = id
        self.name = name
        self.avatar = avatar
        self.join_date = join_date
        self.profile_color = profile_color
        self.linkedin = linkedin
        self.bio = bio
        
        Member.all.append(self)
    
    def change_desc(self, new_desc:str):
        self._desc = new_desc
    
    def find(id=None, name=None) -> discord.User:
        """_summary_

        Args:
            id (_type_, optional): _description_. Defaults to None.
            name (_type_, optional): _description_. Defaults to None.

        Returns:
            discord.User: _description_
        """
        
        if id:
            for student in Member.all:
                if student._id == id:
                    return student
        
        if name:
            for student in Member.all:
                if student.name.lower() == name.lower():
                    return student
        
    def json_format(self) -> dict:
        return {self.name:
                {"id": str(self._id),
                "name": self.name,
                "bio": self.bio,
                "linkedin": self.linkedin,
                "avatar": str(self.avatar),
                "join_date": str(self.join_date),
                "profile_color": str(self.profile_color)}}
        
        
                
        
def test():
    example_dict = {"id": "284852323472113664",
                    "desc": "",
                    "name": "Brunden",
                    "avatar": "https://cdn.discordapp.com/avatars/284852323472113664/b8d78c6d7b7f3b5b445aa8f5d43dd61a.png?size=1024",
                    "join_date": "2024-08-27 02:43:26.991481+00:00",
                    "profile_color": "None"}

    member = Member(**example_dict)
