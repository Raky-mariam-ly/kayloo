"""Utilitaire d'envoi d'email via SMTP standard (smtplib + asyncio.to_thread)."""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import get_settings

logger = logging.getLogger(__name__)


def _send_smtp(to: str, subject: str, html_body: str) -> None:
    """Envoi synchrone — exécuté dans un thread pour ne pas bloquer l'event loop."""
    settings = get_settings()

    if not settings.smtp_user or not settings.smtp_password:
        logger.warning(
            "SMTP non configuré — email simulé en mode dev.\n"
            "  À      : %s\n"
            "  Sujet  : %s\n"
            "  Contenu: (voir le lien ci-dessous si c'est un reset password)",
            to, subject,
        )
        # En dev : extraire et afficher le lien de réinitialisation depuis le corps HTML
        import re
        links = re.findall(r'href="(http[^"]+reset-password[^"]*)"', html_body)
        if links:
            logger.warning("  --> LIEN DE RÉINITIALISATION : %s", links[0])
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.smtp_from
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.sendmail(settings.smtp_from, to, msg.as_string())

    logger.info("Email envoyé à %s — sujet : %s", to, subject)


async def send_email(to: str, subject: str, html_body: str) -> None:
    """Envoie un email HTML de manière asynchrone (thread pool)."""
    await asyncio.to_thread(_send_smtp, to, subject, html_body)


async def send_reset_password_email(to: str, full_name: str, reset_url: str) -> None:
    """Email de réinitialisation de mot de passe."""
    subject = "Réinitialisation de votre mot de passe — Kayloo"
    html_body = f"""
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">

          <!-- Header -->
          <tr>
            <td style="background:#a80000;padding:28px 40px;text-align:center;">
              <span style="color:#fff;font-size:22px;font-weight:700;letter-spacing:.5px;">KAYLOO</span>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="font-size:16px;color:#1a1a2e;margin:0 0 16px;">
                Bonjour <strong>{full_name}</strong>,
              </p>
              <p style="font-size:14px;color:#495057;margin:0 0 24px;line-height:1.6;">
                Un administrateur a demandé la réinitialisation de votre mot de passe.<br>
                Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe.
              </p>

              <div style="text-align:center;margin:32px 0;">
                <a href="{reset_url}"
                   style="display:inline-block;background:#a80000;color:#fff;text-decoration:none;
                          padding:14px 36px;border-radius:6px;font-weight:700;font-size:15px;">
                  Réinitialiser mon mot de passe
                </a>
              </div>

              <p style="font-size:12px;color:#868e96;margin:24px 0 0;line-height:1.5;">
                Ce lien est valable <strong>1 heure</strong>.<br>
                Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
              </p>

              <hr style="border:none;border-top:1px solid #f1f3f5;margin:24px 0;">
              <p style="font-size:11px;color:#adb5bd;margin:0;">
                Vous ne pouvez pas cliquer sur le bouton ?
                Copiez ce lien dans votre navigateur :<br>
                <a href="{reset_url}" style="color:#a80000;word-break:break-all;">{reset_url}</a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f9fa;padding:18px 40px;text-align:center;">
              <p style="font-size:11px;color:#adb5bd;margin:0;">
                © Kayloo · contact@kayloo.immo
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    await send_email(to, subject, html_body)
