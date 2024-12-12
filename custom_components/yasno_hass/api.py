# Yasno API Client

import logging
import requests

from homeassistant.helpers.update_coordinator import UpdateFailed

from .models import YasnoAPIResponse

_LOGGER = logging.getLogger(__name__)


class YasnoAPIClient:
    """
    Fetch data from Yasno API
    """

    _api_url = (
        "https://api.yasno.com.ua/api/v1/pages/home/schedule-turn-off-electricity"
    )
    _TEMPLATE_NAME = "electricity-outages-daily-schedule"

    def update(self, force=False) -> dict:
        _LOGGER.info("Performing Yasno API call...")
        try:
            resp = requests.get(self._api_url)
            if resp.status_code != 200:
                _LOGGER.error(f"failed API response {resp.status_code}:{resp.content}")
                return None

            resp_json = resp.json()

            components = YasnoAPIResponse(**resp_json).components
            daily_schedule_components = [
                s.dailySchedule
                for s in components
                if s.template_name == self._TEMPLATE_NAME
            ]
            if len(daily_schedule_components) >= 1:
                _LOGGER.debug(
                    f"Found {len(daily_schedule_components)} daily schedule(s). Taking first."
                )
                return daily_schedule_components.pop()

            raise UpdateFailed("No daily schedules found in API response.")

        except Exception as e:
            _LOGGER.exception(f"Error calling Yasno API: {e}")
            return None


client = YasnoAPIClient()
