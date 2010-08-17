#include <stdio.h>
#include <swk.h>

static SwkBox weather[] = {
	{ .cb=swk_entry, .text="" },
	{ .cb=swk_button, .text="add" },
	{ .cb=swk_button, .text="refresh" },
	SWK_BOX_NEWLINE(-1),
	{ .cb=swk_label, .text="Barcelona" },
	{ .cb=swk_button, .text="remove" },
	SWK_BOX_NEWLINE(2),
	{ .cb=swk_image, .text="../img/rain.png" },
	{ .cb=swk_label, .text="Monday" },
	{ .cb=swk_label, .text="23-27" },
	SWK_BOX_NEWLINE(1),
	{ .cb=swk_image, .text="../img/sun.png" },
	{ .cb=swk_label, .text="Tuesday" },
	{ .cb=swk_label, .text="28-32" },
	SWK_BOX_NEWLINE(1),
	{ .cb=swk_image, .text="../img/snow.png" },
	{ .cb=swk_label, .text="Wednesday" },
	{ .cb=swk_label, .text="0-5" },

	SWK_BOX_NEWLINE(1),
	{ .cb=swk_separator },
	SWK_BOX_NEWLINE(1),

	{ .cb=swk_label, .text="Paris" },
	{ .cb=swk_button, .text="remove" },
	SWK_BOX_NEWLINE(2),
	{ .cb=swk_image, .text="../img/rain.png" },
	{ .cb=swk_label, .text="Monday" },
	{ .cb=swk_label, .text="23-27" },
	SWK_BOX_NEWLINE(1),
	{ .cb=swk_image, .text="../img/rain-light.png" },
	{ .cb=swk_label, .text="Tuesday" },
	{ .cb=swk_label, .text="28-32" },
	SWK_BOX_NEWLINE(1),
	{ .cb=swk_image, .text="../img/sun.png" },
	{ .cb=swk_label, .text="Wednesday" },
	{ .cb=swk_label, .text="0-5" },
	{ .cb=NULL }
};

int main() {
	SwkWindow w = {
		.title = "Weather",
		.boxes = { weather, NULL },
		.box = weather
	};
	if (!swk_use(&w))
		return 1;
	swk_loop();
	return 0;
}
