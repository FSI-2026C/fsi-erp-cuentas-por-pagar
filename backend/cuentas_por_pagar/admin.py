from django.contrib import admin
from .models import (
    TipoComprobante, Moneda, MedioPago, Banco,
    Proveedor, Obligacion, Pago, ReversoPago, RefCompra,
)


@admin.register(TipoComprobante)
class TipoComprobanteAdmin(admin.ModelAdmin):
    list_display = ("doc_tip_cod", "doc_tip_des", "doc_tip_est_reg")
    search_fields = ("doc_tip_cod", "doc_tip_des")
    list_filter = ("doc_tip_est_reg",)


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ("mon_cod", "mon_des", "mon_est_reg")
    list_filter = ("mon_est_reg",)


@admin.register(MedioPago)
class MedioPagoAdmin(admin.ModelAdmin):
    list_display = ("med_cod", "med_des", "med_est_reg")
    list_filter = ("med_est_reg",)


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ("ban_cod", "ban_des", "ban_est_reg")
    list_filter = ("ban_est_reg",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("prv_cod", "prv_nom", "prv_doc_tip", "prv_doc_num", "prv_est_reg")
    search_fields = ("prv_cod", "prv_nom", "prv_doc_num")
    list_filter = ("prv_est_reg", "prv_doc_tip")


@admin.register(Obligacion)
class ObligacionAdmin(admin.ModelAdmin):
    list_display = (
        "obl_cod", "proveedor", "tipo_comprobante",
        "obl_doc_ser", "obl_doc_num", "obl_fec_emi", "obl_fec_ven",
        "moneda", "obl_imp", "obl_reg_act",
    )
    search_fields = ("obl_cod", "obl_doc_num", "proveedor__prv_nom")
    list_filter = ("moneda", "tipo_comprobante", "obl_fec_emi")
    readonly_fields = ("obl_reg_ins",)
    date_hierarchy = "obl_fec_emi"


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "pag_cod", "obligacion", "pag_fec", "pag_imp",
        "medio_pago", "banco", "pag_reg_act",
    )
    search_fields = ("pag_cod", "obligacion__obl_cod")
    list_filter = ("medio_pago", "banco")
    readonly_fields = ("pag_reg_ins",)


@admin.register(ReversoPago)
class ReversoPagoAdmin(admin.ModelAdmin):
    list_display = ("pago", "rev_mot", "rev_reg_ins", "rev_reg_act")
    search_fields = ("pago__pag_cod",)
    readonly_fields = ("rev_reg_ins",)


@admin.register(RefCompra)
class RefCompraAdmin(admin.ModelAdmin):
    list_display = ("obligacion", "ref_tip", "ref_ext")
    list_filter = ("ref_tip",)
    search_fields = ("obligacion__obl_cod", "ref_ext")
