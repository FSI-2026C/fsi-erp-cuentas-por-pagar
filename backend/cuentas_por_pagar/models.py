from django.db import models


# ---------------------------------------------------------------------------
# Tablas referenciales (catálogos)
# ---------------------------------------------------------------------------

class TipoComprobante(models.Model):
    """F1Z_TIPO_COMPROBANTE — Tipos documentales que sustentan una obligación."""

    doc_tip_cod = models.CharField(
        "Código tipo comprobante", max_length=32, primary_key=True
    )
    doc_tip_des = models.CharField("Descripción tipo", max_length=200)
    doc_tip_est_reg = models.CharField(
        "Estado de registro", max_length=1,
        choices=[("A", "Activo"), ("I", "Inactivo"), ("*", "Reservado")],
    )

    class Meta:
        db_table = "f1z_tipo_comprobante"
        verbose_name = "Tipo de comprobante"
        verbose_name_plural = "Tipos de comprobante"

    def __str__(self):
        return f"{self.doc_tip_cod} — {self.doc_tip_des}"


class Moneda(models.Model):
    """F1Z_MONEDA — Monedas utilizadas para registrar obligaciones."""

    mon_cod = models.CharField(
        "Código moneda", max_length=3, primary_key=True
    )
    mon_des = models.CharField("Descripción moneda", max_length=200)
    mon_est_reg = models.CharField(
        "Estado de registro", max_length=1,
        choices=[("A", "Activo"), ("I", "Inactivo"), ("*", "Reservado")],
    )

    class Meta:
        db_table = "f1z_moneda"
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

    def __str__(self):
        return f"{self.mon_cod} — {self.mon_des}"


class MedioPago(models.Model):
    """F1Z_MEDIO_PAGO — Medios utilizados en el registro de pagos."""

    med_cod = models.CharField(
        "Código medio", max_length=32, primary_key=True
    )
    med_des = models.CharField("Descripción medio", max_length=200)
    med_est_reg = models.CharField(
        "Estado de registro", max_length=1,
        choices=[("A", "Activo"), ("I", "Inactivo"), ("*", "Reservado")],
    )

    class Meta:
        db_table = "f1z_medio_pago"
        verbose_name = "Medio de pago"
        verbose_name_plural = "Medios de pago"

    def __str__(self):
        return f"{self.med_cod} — {self.med_des}"


class Banco(models.Model):
    """F1Z_BANCO — Bancos asociados a los pagos por transferencia."""

    ban_cod = models.CharField(
        "Código banco", max_length=32, primary_key=True
    )
    ban_des = models.CharField("Descripción banco", max_length=200)
    ban_est_reg = models.CharField(
        "Estado de registro", max_length=1,
        choices=[("A", "Activo"), ("I", "Inactivo"), ("*", "Reservado")],
    )

    class Meta:
        db_table = "f1z_banco"
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"

    def __str__(self):
        return f"{self.ban_cod} — {self.ban_des}"


# ---------------------------------------------------------------------------
# Tabla maestra
# ---------------------------------------------------------------------------

class Proveedor(models.Model):
    """F1M_PROVEEDOR — Proveedores vinculados a las obligaciones."""

    prv_cod = models.CharField(
        "Código de proveedor", max_length=64, primary_key=True
    )
    prv_doc_tip = models.CharField("Tipo de identidad", max_length=32)
    prv_doc_num = models.CharField("Número de identidad", max_length=64)
    prv_nom = models.CharField("Nombre de proveedor", max_length=200)
    prv_est_reg = models.CharField(
        "Estado del registro", max_length=1,
        choices=[("A", "Activo"), ("I", "Inactivo"), ("*", "Reservado")],
    )

    class Meta:
        db_table = "f1m_proveedor"
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        constraints = [
            models.UniqueConstraint(
                fields=["prv_doc_tip", "prv_doc_num"],
                name="uq_proveedor_identidad",
            )
        ]

    def __str__(self):
        return f"{self.prv_cod} — {self.prv_nom}"


# ---------------------------------------------------------------------------
# Tablas transaccionales
# ---------------------------------------------------------------------------

class Obligacion(models.Model):
    obl_cod = models.CharField(
        "Código obligación", max_length=64, primary_key=True
    )
    obl_sol_cod = models.CharField(
        "Token de alta", max_length=64, unique=True,
        help_text="Idempotencia: reenviar el mismo token no crea una nueva obligación.",
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT,
        db_column="prv_cod", verbose_name="Proveedor",
    )
    tipo_comprobante = models.ForeignKey(
        TipoComprobante, on_delete=models.PROTECT,
        db_column="doc_tip_cod", verbose_name="Tipo de comprobante",
    )
    obl_doc_ser = models.CharField(
        "Serie comprobante", max_length=64, blank=True, default="",
        help_text="Vacío si el tipo de comprobante no requiere serie.",
    )
    obl_doc_num = models.CharField("Número comprobante", max_length=64)
    obl_fec_emi = models.DateField("Fecha de emisión")
    obl_fec_ven = models.DateField("Fecha de vencimiento")
    moneda = models.ForeignKey(
        Moneda, on_delete=models.PROTECT,
        db_column="mon_cod", verbose_name="Moneda",
    )
    obl_imp = models.DecimalField(
        "Importe obligación", max_digits=14, decimal_places=2,
    )
    obl_reg_ins = models.DateTimeField(
        "Instante de registro", auto_now_add=True,
        help_text="Generado por el servidor al registrar la obligación.",
    )
    obl_reg_act = models.CharField(
        "Actor del registro", max_length=128,
        help_text="Identificador del usuario o servicio que registró la obligación.",
    )

    class Meta:
        db_table = "f1t_obligacion"
        verbose_name = "Obligación"
        verbose_name_plural = "Obligaciones"
        constraints = [
            models.UniqueConstraint(
                fields=["proveedor", "tipo_comprobante", "obl_doc_ser", "obl_doc_num"],
                name="uq_obligacion_comprobante",
            ),
            models.CheckConstraint(
                condition=models.Q(obl_imp__gt=0),
                name="ck_obligacion_importe_positivo",
            ),
            models.CheckConstraint(
                condition=models.Q(obl_fec_ven__gte=models.F("obl_fec_emi")),
                name="ck_obligacion_vencimiento_valido",
            ),
        ]

    def __str__(self):
        return f"{self.obl_cod} — {self.proveedor_id} / {self.tipo_comprobante_id} {self.obl_doc_ser}-{self.obl_doc_num}"


class Pago(models.Model):
    pag_cod = models.CharField(
        "Código pago", max_length=64, primary_key=True
    )
    pag_sol_cod = models.CharField(
        "Token de pago", max_length=64, unique=True,
        help_text="Idempotencia: una misma solicitud confirmada no produce pagos duplicados.",
    )
    obligacion = models.ForeignKey(
        Obligacion, on_delete=models.PROTECT,
        db_column="obl_cod", verbose_name="Obligación destino",
        related_name="pagos",
    )
    pag_fec = models.DateField("Fecha de pago")
    pag_imp = models.DecimalField(
        "Importe pago", max_digits=14, decimal_places=2,
    )
    medio_pago = models.ForeignKey(
        MedioPago, on_delete=models.PROTECT,
        db_column="med_cod", verbose_name="Medio de pago",
    )
    banco = models.ForeignKey(
        Banco, on_delete=models.PROTECT,
        db_column="ban_cod", verbose_name="Banco referencial",
        null=True, blank=True,
        help_text="Vacío en efectivo; requerido en transferencia.",
    )
    pag_ref_ban = models.CharField(
        "Referencia bancaria", max_length=128, blank=True, default="",
        help_text="Requerida en transferencias; vacía en efectivo.",
    )
    pag_reg_ins = models.DateTimeField(
        "Instante registro pago", auto_now_add=True,
    )
    pag_reg_act = models.CharField("Actor del pago", max_length=128)

    class Meta:
        db_table = "f1t_pago"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pag_imp__gt=0),
                name="ck_pago_importe_positivo",
            ),
        ]

    def __str__(self):
        return f"{self.pag_cod} — {self.obligacion_id}"


class ReversoPago(models.Model):
    pago = models.OneToOneField(
        Pago, on_delete=models.PROTECT,
        primary_key=True, db_column="pag_cod",
        verbose_name="Pago revertido",
        related_name="reverso",
    )
    rev_sol_cod = models.CharField(
        "Token de reverso", max_length=64, unique=True,
        help_text="Idempotencia: repetir el reverso de la misma solicitud no duplica su efecto.",
    )
    rev_mot = models.CharField("Motivo reversión", max_length=500)
    rev_reg_ins = models.DateTimeField(
        "Instante reversión", auto_now_add=True,
    )
    rev_reg_act = models.CharField("Actor reversión", max_length=128)

    class Meta:
        db_table = "f1t_reverso_pago"
        verbose_name = "Reverso de pago"
        verbose_name_plural = "Reversos de pago"

    def __str__(self):
        return f"Reverso de {self.pago_id}"


class RefCompra(models.Model):
    TIPO_RECURSO_CHOICES = [
        ("OC", "Orden de compra"),
        ("OC_LINEA", "Línea de orden de compra"),
        ("RECEPCION", "Recepción"),
        ("RECEPCION_LINEA", "Línea de recepción"),
        ("CONFORMIDAD", "Conformidad"),
    ]

    obligacion = models.ForeignKey(
        Obligacion, on_delete=models.PROTECT,
        db_column="obl_cod", verbose_name="Obligación vinculada",
        related_name="referencias_compra",
    )
    ref_tip = models.CharField(
        "Tipo de recurso", max_length=32, choices=TIPO_RECURSO_CHOICES,
    )
    ref_ext = models.CharField(
        "Identificador externo", max_length=128,
        help_text="ID opaco y estable del recurso en Compras; sin FK física.",
    )

    class Meta:
        db_table = "f1t_ref_compra"
        verbose_name = "Referencia a Compras"
        verbose_name_plural = "Referencias a Compras"
        constraints = [
            models.UniqueConstraint(
                fields=["obligacion", "ref_tip", "ref_ext"],
                name="uq_ref_compra_pk",
            ),
        ]

    def __str__(self):
        return f"{self.obligacion_id} / {self.ref_tip} / {self.ref_ext}"
