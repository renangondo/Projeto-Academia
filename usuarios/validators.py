from django.contrib.auth.password_validation import MinimumLengthValidator
from django.core.exceptions import ValidationError


class TamanhoMinimoValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"Esta senha é muito curta. Ela precisa ter pelo menos {self.min_length} caracteres.",
                code="password_too_short",
            )

    def get_help_text(self):
        return f"Sua senha precisa ter pelo menos {self.min_length} caracteres."