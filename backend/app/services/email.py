"""Email service for sending resource lists."""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.resource import ResourceRead

logger = logging.getLogger(__name__)


def format_resources_html(resources: list["ResourceRead"]) -> str:
    """Format resources as HTML email content."""
    html_parts = [
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Saved Resources - Vibe4Vets</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
                h1 { color: #1e3a5f; border-bottom: 3px solid #c9a227; padding-bottom: 10px; }
                .resource { background: #f8f9fa; border-left: 4px solid #c9a227; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
                .resource h2 { color: #1e3a5f; margin: 0 0 5px 0; font-size: 18px; }
                .resource .org { color: #666; font-size: 14px; margin-bottom: 10px; }
                .resource .contact { font-size: 14px; }
                .resource .contact a { color: #c9a227; }
                .resource .categories { margin-top: 10px; }
                .resource .category { display: inline-block; background: #e8f4f8; color: #1e3a5f; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }
                .resource .description { color: #555; font-size: 14px; margin-top: 10px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #888; text-align: center; }
            </style>
        </head>
        <body>
            <h1>Your Saved Resources</h1>
            <p>Here are the resources you saved from Vibe4Vets:</p>
        """
    ]

    for resource in resources:
        phone_html = f'<a href="tel:{resource.phone}">{resource.phone}</a>' if resource.phone else ""
        website_html = f'<a href="{resource.website}">{resource.website}</a>' if resource.website else ""
        contact_parts = [p for p in [phone_html, website_html] if p]
        contact_html = f'<div class="contact">{" | ".join(contact_parts)}</div>' if contact_parts else ""

        categories_html = "".join(
            f'<span class="category">{cat.title()}</span>'
            for cat in resource.categories
        )

        location_text = ""
        if resource.scope == "national":
            location_text = "Nationwide"
        elif resource.states:
            location_text = ", ".join(resource.states)

        if location_text:
            categories_html += f'<span class="category">{location_text}</span>'

        description = resource.summary or resource.description
        if len(description) > 200:
            description = description[:200] + "..."

        html_parts.append(f"""
            <div class="resource">
                <h2>{resource.title}</h2>
                <div class="org">{resource.organization.name if resource.organization else ''}</div>
                {contact_html}
                <div class="categories">{categories_html}</div>
                <div class="description">{description}</div>
            </div>
        """)

    html_parts.append("""
            <div class="footer">
                <p>Sent from <a href="https://vibe4vets.com" style="color: #c9a227;">Vibe4Vets</a> - Veteran Resource Directory</p>
                <p>This email was sent because you requested your saved resources be emailed to you.</p>
            </div>
        </body>
        </html>
    """)

    return "".join(html_parts)


def format_resources_text(resources: list["ResourceRead"]) -> str:
    """Format resources as plain text email content."""
    lines = [
        "YOUR SAVED RESOURCES FROM VIBE4VETS",
        "=" * 40,
        "",
    ]

    for i, resource in enumerate(resources, 1):
        lines.append(f"{i}. {resource.title}")
        if resource.organization:
            lines.append(f"   Organization: {resource.organization.name}")
        if resource.phone:
            lines.append(f"   Phone: {resource.phone}")
        if resource.website:
            lines.append(f"   Website: {resource.website}")
        lines.append(f"   Categories: {', '.join(resource.categories)}")
        if resource.scope == "national":
            lines.append("   Coverage: Nationwide")
        elif resource.states:
            lines.append(f"   States: {', '.join(resource.states)}")

        description = resource.summary or resource.description
        if len(description) > 150:
            description = description[:150] + "..."
        lines.append(f"   {description}")
        lines.append("")

    lines.extend([
        "-" * 40,
        "Sent from Vibe4Vets - https://vibe4vets.com",
        "Veteran Resource Directory",
    ])

    return "\n".join(lines)


def send_resources_email(email: str, resources: list["ResourceRead"]) -> bool:
    """Send resources email using SMTP.

    Requires environment variables:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port (default: 587)
    - SMTP_USER: SMTP username
    - SMTP_PASSWORD: SMTP password
    - SMTP_FROM: From email address

    If SMTP is not configured, logs the email content instead.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", "noreply@vibe4vets.com")

    # Create email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your Saved Resources ({len(resources)} items) - Vibe4Vets"
    msg["From"] = smtp_from
    msg["To"] = email

    # Add plain text and HTML parts
    text_content = format_resources_text(resources)
    html_content = format_resources_html(resources)

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Check if SMTP is configured
    if not smtp_host or not smtp_user or not smtp_password:
        logger.warning(
            "SMTP not configured. Email would have been sent to %s with %d resources. "
            "Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD environment variables to enable email.",
            email,
            len(resources),
        )
        logger.debug("Email content (text):\n%s", text_content)
        return True  # Return True to not fail the request

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, [email], msg.as_string())

        logger.info("Email sent successfully to %s with %d resources", email, len(resources))
        return True

    except Exception as e:
        logger.error("Failed to send email to %s: %s", email, str(e))
        return False
