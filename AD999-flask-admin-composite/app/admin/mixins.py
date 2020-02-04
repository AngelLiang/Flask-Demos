from flask import url_for
from sqlalchemy import desc
from app.models import Alert


class AlertsMixin(object):

    @property
    def alerts(self):
        alerts = Alert.query.order_by(desc(Alert.created_at)).limit(3).all()
        for alert in alerts:
            setattr(alert, 'url', url_for('alert.details_view', id=alert.id))
        return alerts
