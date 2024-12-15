# yasno_hass
Minimalistic Yasno API parser to monitor power outages


URL: https://api.yasno.com.ua/api/v1/pages/home/schedule-turn-off-electricity
Sample API response (parsed part):

```JSON
{
  "page": {},
  "components": [
      {
        "template_name": "electricity-outages-daily-schedule",
        "anchor": "electricity-outages-daily-schedule_id_MTQw",
        "available_regions": [
          "dnipro",
          "kiev"
        ],
        "title": "Графік відключень",
        "description": null,
        "schedule": {
          ...
        },
        "lastRegistryUpdateTime": 1733761471,
        "cities": null,
        "streets": null,
        "dailySchedule": {
          "kiev": {
            "today": {
              "title": "Вівторок, 10.12.2024 на 00:00",
              "groups": {
                "1.1": [
                  {
                    "start": 8,
                    "end": 8.5,
                    "type": "DEFINITE_OUTAGE"
                  },
                  {
                    "start": 8.5,
                    "end": 9,
                    "type": "DEFINITE_OUTAGE"
                  },
                  ...
                  {
                    "start": 10.5,
                    "end": 11,
                    "type": "DEFINITE_OUTAGE"
                  },
                  {
                    "start": 18,
                    "end": 18.5,
                    "type": "DEFINITE_OUTAGE"
                  },
                ],
                "2...6": [ the same ]
              }
            },
            "tomorrow": [ same structure but seems to be optional ]
          },
          
          "dnipro": { same structure }
        }
      }
  ]
}
```

Added binary sensors, one per city/group

Added calendars for today/tomorrow per city/group
