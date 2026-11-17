import pytest
from cuentas_por_pagar.models import Moneda


@pytest.mark.django_db
def test_moneda_se_crea_y_recupera():
    Moneda.objects.create(mon_cod="PEN", mon_des="Sol peruano", mon_est_reg="A")
    moneda = Moneda.objects.get(mon_cod="PEN")
    assert moneda.mon_des == "Sol peruano"
    assert moneda.mon_est_reg == "A"
