import frappe


@frappe.whitelist()
def get_contact_list(
    txt, page_length=20, extra_filters: str | None = None
) -> list[dict]:
    """
    Return email ids for a multiselect field.
    It allows users to also search based on the Dynamic Link in the
    Contact document so that it is possible to type the name of a
    Supplier and all emails for Contacts linked to the Supplier will
    be returned
    """
    if extra_filters:
        extra_filters = frappe.parse_json(extra_filters)

    filters = [
        ["Contact Email", "email_id", "is", "set"],
    ]
    if extra_filters:
        filters.extend(extra_filters)

    fields = ["first_name", "middle_name", "last_name", "company_name"]
    contacts = frappe.get_list(
        "Contact",
        fields=[
            "full_name",
            "`tabContact Email`.email_id",
            "`tabDynamic Link`.link_name",
        ],
        filters=filters,
        or_filters=[[field, "like", f"%{txt}%"] for field in fields]
        + [
            ["Contact Email", "email_id", "like", f"%{txt}%"],
            ["Dynamic Link", "link_name", "like", f"%{txt}%"],
        ],
        limit_page_length=page_length,
    )

    # The multiselect field will store the `label` as the selected value.
    # The `value` is just used as a unique key to distinguish between the options.
    # https://github.com/frappe/frappe/blob/6c6a89bcdd9454060a1333e23b855d0505c9ebc2/frappe/public/js/frappe/form/controls/autocomplete.js#L29-L35
    return [
        frappe._dict(
            value=d.email_id,
            label=d.email_id,
            description=d.full_name + f" {f'({d.link_name})' if d.link_name else ''}",
        )
        for d in contacts
    ]
