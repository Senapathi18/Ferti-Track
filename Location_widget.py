# modules/location_widget.py — Database-powered AP location widget

import customtkinter as ctk
from database import (get_all_districts, get_mandals_for_district,
                      get_villages_for_mandal, search_villages_db,
                      is_villages_populated, add_village)


class APLocationWidget(ctk.CTkFrame):
    """
    3-level location picker powered by your database.
    District → Mandal → Village (search as you type)
    """
    def __init__(self, parent, width=360, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.width = width
        self._current_district = ""
        self._current_mandal = ""
        self._build()

    def _build(self):
        # State (fixed)
        ctk.CTkLabel(self, text="State: Andhra Pradesh ✅",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#0f6e56").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(0, 6))

        # District
        ctk.CTkLabel(self, text="District *",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#333").grid(
            row=1, column=0, sticky="w", padx=4, pady=(0, 2))

        districts = get_all_districts()
        self.district_dd = ctk.CTkComboBox(
            self, values=districts if districts else ["Run populate_villages.py first"],
            width=self.width, command=self._on_district_change,
            font=ctk.CTkFont(size=13))
        self.district_dd.set("Select District")
        self.district_dd.grid(row=2, column=0, columnspan=2, sticky="w",
                              padx=4, pady=(0, 8))

        # Mandal
        ctk.CTkLabel(self, text="Mandal *",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#333").grid(
            row=3, column=0, sticky="w", padx=4, pady=(0, 2))

        self.mandal_dd = ctk.CTkComboBox(
            self, values=["Select district first"],
            width=self.width, command=self._on_mandal_change,
            font=ctk.CTkFont(size=13))
        self.mandal_dd.set("Select district first")
        self.mandal_dd.grid(row=4, column=0, columnspan=2, sticky="w",
                            padx=4, pady=(0, 8))

        # Village search
        ctk.CTkLabel(self, text="Village / Town *",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#333").grid(
            row=5, column=0, sticky="w", padx=4, pady=(0, 2))

        self.village_entry = ctk.CTkEntry(
            self, placeholder_text="Type village name to search...",
            width=self.width - 50, font=ctk.CTkFont(size=13))
        self.village_entry.grid(row=6, column=0, sticky="w", padx=4, pady=(0, 4))
        self.village_entry.bind("<KeyRelease>", self._on_village_type)

        # Add village button (if not found in list)
        ctk.CTkButton(self, text="+ Add", width=44,
                     fg_color="#0f6e56", hover_color="#0a5443",
                     font=ctk.CTkFont(size=11),
                     command=self._add_new_village).grid(
            row=6, column=1, padx=(4, 4), pady=(0, 4))

        # Suggestions dropdown
        self.suggestion_frame = ctk.CTkScrollableFrame(
            self, width=self.width - 20, height=0,
            fg_color="#f0f8ff", border_width=1, border_color="#cce")
        self.suggestion_frame.grid(row=7, column=0, columnspan=2,
                                   sticky="w", padx=4, pady=(0, 4))

        # Village count hint
        self.hint_label = ctk.CTkLabel(
            self, text="", text_color="gray",
            font=ctk.CTkFont(size=10))
        self.hint_label.grid(row=8, column=0, sticky="w", padx=4)

    def _on_district_change(self, choice):
        self._current_district = choice
        self._current_mandal = ""
        mandals = get_mandals_for_district(choice)
        self.mandal_dd.configure(values=mandals if mandals else ["No mandals found"])
        self.mandal_dd.set("Select Mandal")
        self.village_entry.delete(0, "end")
        self.hint_label.configure(text="")
        self._hide_suggestions()

    def _on_mandal_change(self, choice):
        self._current_mandal = choice
        self.village_entry.delete(0, "end")
        self._hide_suggestions()
        villages = get_villages_for_mandal(self._current_district, choice)
        count = len(villages)
        self.hint_label.configure(
            text=f"{count} villages in {choice} — type to search")

    def _on_village_type(self, event=None):
        query = self.village_entry.get().strip()
        if not self._current_district or not self._current_mandal:
            return
        if len(query) < 1:
            self._hide_suggestions()
            return
        matches = search_villages_db(
            self._current_district, self._current_mandal, query)
        self._show_suggestions(matches)

    def _show_suggestions(self, villages):
        for w in self.suggestion_frame.winfo_children():
            w.destroy()

        if not villages:
            ctk.CTkLabel(self.suggestion_frame,
                        text="No match — type your village name and click '+ Add'",
                        text_color="gray",
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=4, pady=2)
            self.suggestion_frame.configure(height=32)
        else:
            for v in villages[:10]:
                ctk.CTkButton(
                    self.suggestion_frame, text=v, anchor="w",
                    fg_color="transparent", text_color="#1a1a1a",
                    hover_color="#dce6f0", height=30,
                    font=ctk.CTkFont(size=12),
                    command=lambda village=v: self._select_village(village)
                ).pack(fill="x", padx=2, pady=1)
            self.suggestion_frame.configure(height=min(len(villages), 10) * 34)

    def _hide_suggestions(self):
        for w in self.suggestion_frame.winfo_children():
            w.destroy()
        self.suggestion_frame.configure(height=0)

    def _select_village(self, village):
        self.village_entry.delete(0, "end")
        self.village_entry.insert(0, village)
        self._hide_suggestions()

    def _add_new_village(self):
        """Adds a new village to the database if it's not already there."""
        village = self.village_entry.get().strip()
        if not village:
            return
        if not self._current_district or not self._current_mandal:
            return
        add_village(self._current_district, self._current_mandal, village)
        self.hint_label.configure(
            text=f"✅ '{village}' added to {self._current_mandal}",
            text_color="#0f6e56")
        self._hide_suggestions()

    def get_location(self):
        return (
            self.district_dd.get(),
            self.mandal_dd.get(),
            self.village_entry.get().strip()
        )

    def validate(self):
        district, mandal, village = self.get_location()
        if district == "Select District":
            return False, "Please select a District."
        if mandal in ("Select district first", "Select Mandal"):
            return False, "Please select a Mandal."
        if not village:
            return False, "Please type a Village name."
        return True, ""