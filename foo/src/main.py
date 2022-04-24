from typing import cast

import requests
from dataclasses import dataclass, field
from datetime import datetime


class RickAndMortyObjects:
    pass


@dataclass
class Location(RickAndMortyObjects):
    url: str
    name: str
    id: int = -1
    type: str = ''
    dimension: str = ''
    residents: list['Character'] = field(default_factory=list['Character'])
    created: datetime = datetime.today()
    is_initialized: bool = False

    @staticmethod
    def createLocationByUrl(url: str) -> 'Location':
        row_location = requests.get(url).json()
        character = cast(Location, load_rick_and_morty_object(row_location, 'location'))
        return character

    @staticmethod
    def createAnInitLocation(url: str, name: str) -> 'Location':
        location = Location(url=url, name=name)
        return location

    def initialization(self) -> bool:
        if not self.url:
            self.dimension = ''
            return False

        row_location = requests.get(self.url).json()
        character = cast(Location, load_rick_and_morty_object(row_location, 'location'))

        self.url = character.url
        self.id = character.id
        self.name = character.name
        self.type = character.type
        self.dimension = character.dimension
        self.residents = character.residents
        self.created = character.created
        self.is_initialized = character.is_initialized

        return self.is_initialized


@dataclass
class Character(RickAndMortyObjects):
    url: str
    id: int = -1
    name: str = ''
    status: str = ''
    species: str = ''
    type: str = ''
    gender: str = ''
    origin: 'Location' = None
    location: 'Location' = None
    image: str = ''
    episode: list['Episode'] = field(default_factory=list['Episode'])
    created: datetime = datetime.today()
    is_initialized: bool = False

    @staticmethod
    def createCharacterByUrl(url: str) -> 'Character':
        row_character = requests.get(url).json()
        character = cast(Character, load_rick_and_morty_object(row_character, 'character'))
        return character

    @staticmethod
    def createAnInitCharacter(url: str) -> 'Character':
        character = Character(url=url)
        return character

    def initialization(self) -> bool:
        row_character = requests.get(self.url).json()
        character = cast(Character, load_rick_and_morty_object(row_character, 'character'))

        self.url = character.url
        self.id = character.id
        self.name = character.name
        self.status = character.status
        self.species = character.species
        self.type = character.type
        self.gender = character.gender
        self.origin = character.origin
        self.location = character.location
        self.image = character.image
        self.episode = character.episode
        self.created = character.created
        self.is_initialized = character.is_initialized

        return self.is_initialized


@dataclass
class Episode(RickAndMortyObjects):
    url: str
    id: int = -1
    name: str = ''
    air_date: str = ''
    episode: str = ''
    created: datetime = datetime.today()
    characters: list[Character] = field(default_factory=list[Character])
    is_initialized: bool = False

    @staticmethod
    def createEpisodeByUrl(url: str) -> 'Episode':
        row_episode = requests.get(url).json()
        episode = cast(Episode, load_rick_and_morty_object(row_episode, 'episode'))
        return episode

    @staticmethod
    def createAnInitEpisode(url: str) -> 'Episode':
        episode = Episode(url=url)
        return episode

    def initialization(self) -> bool:
        row_episode = requests.get(self.url).json()
        episode = cast(Episode, load_rick_and_morty_object(row_episode, 'episode'))

        self.url = episode.url
        self.id = episode.id
        self.name = episode.name
        self.air_date = episode.air_date
        self.episode = episode.episode
        self.created = episode.created
        self.characters = episode.characters
        self.is_initialized = episode.is_initialized

        return self.is_initialized


@dataclass
class Episodes(RickAndMortyObjects):
    count: str
    next: str | None
    pages: str
    prev: str | None
    episodes: list[Episode] = field(default_factory=list)

    @staticmethod
    def createEpisodesByUrl(url: str) -> 'Episodes':
        row_episodes = requests.get(url).json()
        episodes = cast(Episodes, load_rick_and_morty_object(row_episodes, 'episodes'))
        return episodes

    def getNextEpisodes(self) -> None:
        if self.next is None:
            return

        row_episodes = requests.get(self.next).json()
        episodes = cast(Episodes, load_rick_and_morty_object(row_episodes, 'episodes'))

        self.count = episodes.count
        self.next = episodes.next
        self.pages = episodes.pages
        self.prev = episodes.prev
        self.episodes += episodes.episodes


def _load_episode(ram_object: dict) -> Episode:
    return Episode(
        url=ram_object['url'],
        id=ram_object['id'],
        name=ram_object['name'],
        air_date=ram_object['air_date'],
        episode=ram_object['episode'],
        created=datetime.strptime(ram_object['created'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        characters=[Character.createAnInitCharacter(character) for character in ram_object['characters']],
        is_initialized=True
    )


def _load_episodes(ram_object: dict) -> Episodes:
    return Episodes(
        count=ram_object['info']['count'],
        next=ram_object['info']['next'],
        pages=ram_object['info']['pages'],
        prev=ram_object['info']['prev'],
        episodes=[_load_episode(episode) for episode in ram_object['results']],
        # results=[load_rick_and_morty_object(episode, 'Episodes') for episode in ram_object['results']],
    )


def _load_character(ram_object) -> Character:
    return Character(
        url=ram_object['url'],
        id=ram_object['id'],
        name=ram_object['name'],
        status=ram_object['status'],
        species=ram_object['species'],
        type=ram_object['type'],
        gender=ram_object['gender'],
        origin=Location.createAnInitLocation(ram_object['origin']['url'], ram_object['origin']['name']),
        location=Location.createAnInitLocation(ram_object['location']['url'], ram_object['location']['name']),
        image=ram_object['image'],
        episode=[Episode.createAnInitEpisode(episode) for episode in ram_object['episode']],
        created=datetime.strptime(ram_object['created'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        is_initialized=True
    )


def _load_location(ram_object) -> Location:
    return Location(
        url=ram_object['url'],
        id=ram_object['id'],
        name=ram_object['name'],
        type=ram_object['type'],
        dimension=ram_object['dimension'],
        residents=[Character.createAnInitCharacter(character) for character in ram_object['residents']],
        created=datetime.strptime(ram_object['created'], '%Y-%m-%dT%H:%M:%S.%fZ'),
        is_initialized=True
    )


def load_rick_and_morty_object(ram_object: dict, type_ram_object: str) -> RickAndMortyObjects:
    match type_ram_object:
        case "episodes":
            return _load_episodes(ram_object)
        case "episode":
            return _load_episode(ram_object)
        case "character":
            return _load_character(ram_object)
        case "location":
            return _load_location(ram_object)


def getDimensionsInEpisode(episode: Episode) -> set[str | None]:
    dimensions = set()

    characters = episode.characters
    for character in characters:
        if not character.is_initialized:
            character.initialization()

        origin = character.origin
        if not origin.is_initialized:
            origin.initialization()

        dimensions.add(origin.dimension)

    return dimensions


if __name__ == "__main__":
    episodes = Episodes.createEpisodesByUrl('https://rickandmortyapi.com/api/episode')
    while episodes.next is not None:
        episodes.getNextEpisodes()

    print("list dimensions in episodes rick and morty")
    for episode in episodes.episodes:
        print(f"{episode.episode} {episode.name}", end=': ')
        print(*getDimensionsInEpisode(episode), sep=", ")
