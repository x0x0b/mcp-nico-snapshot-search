from enum import Enum
import httpx
from mcp.server.fastmcp import FastMCP

# Constants
API_ENDPOINT = (
    "https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search"
)
APPLICATION_NAME = "mcp-nico-snapshot-search"

# Initialize FastMCP server
mcp = FastMCP(APPLICATION_NAME)


class SearchTarget(Enum):
    """
    Enum for search targets.

    title: Search in the title.
    description: Search in the description (may return unrelated results)..
    tags: Search in the tags.
    """

    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"


class SortType(Enum):
    """
    Enum for sorting types.

    viewCounter: Sort by view count.
    mylistCounter: Sort by mylist count.
    likeCounter: Sort by like count.
    lengthSeconds: Sort by video length.
    startTime: Sort by publish time.
    lastCommentTime: Sort by the time of the last comment.
    commentCounter: Sort by comment count.
    """

    VIEW_COUNTER_ASC = "+viewCounter"
    MYLIST_COUNTER_ASC = "+mylistCounter"
    LIKE_COUNTER_ASC = "+likeCounter"
    LENGTH_ASC = "+lengthSeconds"
    PUBLISH_TIME_ASC = "+startTime"
    COMMENT_COUNTER_ASC = "+commentCounter"
    LAST_COMMENT_TIME_ASC = "+lastCommentTime"
    VIEW_COUNTER_DESC = "-viewCounter"
    MYLIST_COUNTER_DESC = "-mylistCounter"
    LIKE_COUNTER_DESC = "-likeCounter"
    LENGTH_DESC = "-lengthSeconds"
    PUBLISH_TIME_DESC = "-startTime"
    COMMENT_COUNTER_DESC = "-commentCounter"
    LAST_COMMENT_TIME_DESC = "-lastCommentTime"


def request_api(
    query: str, search_targets: list[SearchTarget], sort_type: SortType
) -> dict:
    """
    Make a request to the NicoNico API and return the response.

    Args:
        query (str): The search query string.
        search_targets (list[SearchTarget]): A list of search targets (e.g., title, tags).
        sort (SortType): The sorting type for the results.

    Returns:
        dict: The API response as a dictionary. Returns an empty list if an error occurs.
    """
    params = {
        "q": query,
        "targets": ",".join([target.value for target in search_targets]),
        "fields": "contentId,title,description,userId,viewCounter,mylistCounter,likeCounter,lengthSeconds,thumbnailUrl,startTime,lastResBody,commentCounter,lastCommentTime,tags,genre",
        "_sort": sort_type.value,
        "_limit": 10,
        "_context": APPLICATION_NAME,
    }
    headers = {
        "User-Agent": APPLICATION_NAME,
    }

    with httpx.Client() as client:
        try:
            response = client.get(API_ENDPOINT, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error occurred while making API request: {e}")
            return []


def append_url(data: dict) -> dict:
    """
    Append the video URL to the data dictionary.

    Args:
        data (dict): The API response data containing video details.

    Returns:
        dict: The updated data with appended video URLs.
    """
    for item in data or []:
        if "contentId" not in item:
            continue
        item["url"] = f"https://nico.ms/{item['contentId']}"
    return data


@mcp.tool()
def search(query: str, search_targets: list[SearchTarget], sort_type: SortType) -> dict:
    """
    Search for videos using the NicoNico API.

    Args:
        query (str): The search query.
                     AND search: Separate with a space (half-width). example: keyword1 keyword2
                     OR search: Separate with OR. example: keyword1 OR keyword2
                     NOT search: Add - before a word. example: keyword1 -keyword2
                     Phrase search: Wrap with double quotes. example: "keyword1 keyword2"
        search_targets (list[SearchTarget]): A list of search targets (e.g., title, tags).
        sort (SortType): The sorting type for the results.

    Returns:
        dict: The search results with appended video URLs.

    Raises:
        ValueError: If the API response indicates an error.
    """
    response = request_api(query, search_targets, sort_type)
    if response.get("meta", {}).get("status", -1) != 200:
        raise ValueError(f"API Error: {response.get('meta', {}).get('message')}")

    return append_url(response.get("data", []))


if __name__ == "__main__":
    mcp.run(transport="stdio")
