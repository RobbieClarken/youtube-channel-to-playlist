from setuptools import setup


setup(
    name="YouTubeChannelToPlaylist",
    version="1.0.1",
    license="MIT",
    author="Robbie Clarken",
    author_email="robbie.clarken@gmail.com",
    url="https://github.com/RobbieClarken/youtube-channel-to-playlist",
    py_modules=["channel_to_playlist"],
    install_requires=["google-api-python-client<1.7.0"],
    entry_points={"console_scripts": ["channel_to_playlist=channel_to_playlist:main"]},
)
