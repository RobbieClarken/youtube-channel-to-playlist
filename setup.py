from setuptools import setup


setup(
    name="YouTubeChannelToPlaylist",
    version="4.0.0",
    license="MIT",
    author="Robbie Clarken",
    author_email="robbie.clarken@gmail.com",
    url="https://github.com/RobbieClarken/youtube-channel-to-playlist",
    py_modules=["channel_to_playlist"],
    install_requires=[
        "google-api-python-client>=2.129.0,<3",
        "google_auth_oauthlib>=1.2.0,<2",
        "python-dateutil>=2.9.0,<3",
    ],
    entry_points={"console_scripts": ["channel_to_playlist=channel_to_playlist:main"]},
)
