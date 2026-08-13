"""Built-in Skills catalog providing core application integrations out-of-the-box.
"""

from typing import List
from app.ai.skills.models import (
    PermissionType,
    SkillCategory,
    SkillManifest,
    VoiceCommandPhrase,
)


def get_builtin_skill_manifests() -> List[SkillManifest]:
    """Generates built-in skill manifests for 27 standard applications and utilities."""
    builtins = [
        # Developer Tools
        SkillManifest(
            skill_id="skill_vscode",
            name="VS Code IDE Skill",
            category=SkillCategory.DEVELOPER_TOOLS,
            description="Open files, debug code, and manage VS Code workspace.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open VS Code", aliases=["Launch VS Code"], examples=["Hey Nova, open VS Code"])
            ],
        ),
        SkillManifest(
            skill_id="skill_git",
            name="Git Version Control Skill",
            category=SkillCategory.DEVELOPER_TOOLS,
            description="Commit changes, push branches, and check Git status.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.NETWORK],
            voice_commands=[
                VoiceCommandPhrase(phrase="Git commit", aliases=["Check git status"], examples=["Hey Nova, git commit changes"])
            ],
        ),
        SkillManifest(
            skill_id="skill_docker",
            name="Docker Container Skill",
            category=SkillCategory.DEVELOPER_TOOLS,
            description="Build images, manage containers, and run Docker compose.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.NETWORK, PermissionType.SYSTEM_SETTINGS],
            voice_commands=[
                VoiceCommandPhrase(phrase="Run Docker container", aliases=["Build docker image"], examples=["Hey Nova, run docker container"])
            ],
        ),
        SkillManifest(
            skill_id="skill_terminal",
            name="Windows Terminal Skill",
            category=SkillCategory.DEVELOPER_TOOLS,
            description="Execute powershell and cmd terminal commands.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open terminal", aliases=["Run command"], examples=["Hey Nova, open terminal"])
            ],
        ),
        SkillManifest(
            skill_id="skill_android",
            name="Android Emulator & ADB Skill",
            category=SkillCategory.DEVELOPER_TOOLS,
            description="Control Android emulator, install APKs, and view logcat.",
            permissions=[PermissionType.DESKTOP, PermissionType.NETWORK],
            voice_commands=[
                VoiceCommandPhrase(phrase="Launch Android emulator", aliases=["Install APK"], examples=["Hey Nova, launch Android emulator"])
            ],
        ),

        # Office Productivity
        SkillManifest(
            skill_id="skill_excel",
            name="Microsoft Excel Skill",
            category=SkillCategory.OFFICE_PRODUCTIVITY,
            description="Enter data, calculate formulas, and process spreadsheets.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open Excel", aliases=["Create spreadsheet"], examples=["Hey Nova, open Excel"])
            ],
        ),
        SkillManifest(
            skill_id="skill_word",
            name="Microsoft Word Skill",
            category=SkillCategory.OFFICE_PRODUCTIVITY,
            description="Format documents, write text, and export PDFs.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open Word", aliases=["Draft document"], examples=["Hey Nova, open Word"])
            ],
        ),
        SkillManifest(
            skill_id="skill_powerpoint",
            name="Microsoft PowerPoint Skill",
            category=SkillCategory.OFFICE_PRODUCTIVITY,
            description="Create slides, edit presentations, and present slideshows.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open PowerPoint", aliases=["Create presentation"], examples=["Hey Nova, open PowerPoint"])
            ],
        ),
        SkillManifest(
            skill_id="skill_outlook",
            name="Microsoft Outlook Skill",
            category=SkillCategory.OFFICE_PRODUCTIVITY,
            description="Send emails, manage inbox, and schedule calendar meetings.",
            permissions=[PermissionType.EMAIL, PermissionType.CALENDAR, PermissionType.NETWORK],
            voice_commands=[
                VoiceCommandPhrase(phrase="Check Outlook emails", aliases=["Schedule meeting"], examples=["Hey Nova, check my emails"])
            ],
        ),

        # Browser & OS
        SkillManifest(
            skill_id="skill_chrome",
            name="Google Chrome Skill",
            category=SkillCategory.BROWSER_OS,
            description="Navigate web pages, search, and manage browser tabs.",
            permissions=[PermissionType.BROWSER, PermissionType.NETWORK],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open Chrome", aliases=["Search web in Chrome"], examples=["Hey Nova, open Chrome"])
            ],
        ),
        SkillManifest(
            skill_id="skill_windows",
            name="Windows System Control Skill",
            category=SkillCategory.BROWSER_OS,
            description="Adjust volume, brightness, and system settings.",
            permissions=[PermissionType.SYSTEM_SETTINGS, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Adjust volume", aliases=["Mute audio"], examples=["Hey Nova, adjust volume"])
            ],
        ),

        # Creative & Media
        SkillManifest(
            skill_id="skill_photoshop",
            name="Adobe Photoshop Skill",
            category=SkillCategory.CREATIVE_MEDIA,
            description="Edit images, crop layers, and export graphics.",
            permissions=[PermissionType.FILESYSTEM, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Open Photoshop", aliases=["Crop image"], examples=["Hey Nova, open Photoshop"])
            ],
        ),
        SkillManifest(
            skill_id="skill_spotify",
            name="Spotify Music Player Skill",
            category=SkillCategory.CREATIVE_MEDIA,
            description="Play music, pause playback, and control playlists.",
            permissions=[PermissionType.NETWORK, PermissionType.DESKTOP],
            voice_commands=[
                VoiceCommandPhrase(phrase="Play Spotify", aliases=["Pause music"], examples=["Hey Nova, play music on Spotify"])
            ],
        ),
    ]

    return builtins
