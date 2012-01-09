#include <SDL.h>
#include <SDL_audio.h>

static Uint8 *audio_chunk;
static Uint32 audio_len;
static Uint8 *audio_pos;

static int t = 0;

static int generate (int i, Uint8 *buf, int len) {
	int n = 0;
printf ("%d %d\n", i, len);
	for (t=i; n<len; t++,n++)
		buf[t] = (t*(((t>>12)|(t>>8))&(63&(t>>4))));
}

/* The audio function callback takes the following parameters:
stream:  A pointer to the audio buffer to be filled
len:     The length (in bytes) of the audio buffer */
static void mixaudio(void *udata, Uint8 *stream, int len) {
	// Only play if we have data left 
	if (audio_len == 0)
		return;
	// Mix as much data as possible 
	//len = ( len > audio_len ? audio_len : len );
	generate (t, audio_pos, len);

	SDL_MixAudio(stream, audio_pos, len, SDL_MIX_MAXVOLUME);
	t += len;
	audio_pos += len;
//	audio_len -= len;
}

int main(int argc, char **argv) {
	SDL_AudioSpec fmt;

// TODO: use 8bit audio here. fuck yeah
	/* Set 16-bit stereo audio at 22Khz */
	fmt.freq = 8000;
	fmt.format = AUDIO_S8;
	fmt.channels = 1;
	fmt.samples = 512;        /* A good value for games */
	fmt.callback = mixaudio;
	fmt.userdata = NULL;

	/* Open the audio device and start playing sound! */
	if (SDL_OpenAudio (&fmt, NULL) < 0) {
		fprintf (stderr, "Unable to open audio: %s\n", SDL_GetError());
		return 1;
	}
	// Load the audio data ... 
{
	audio_len = 4096;
	audio_chunk = malloc (audio_len);
	audio_pos = audio_chunk;
}

	// Let the callback function play the audio chunk 
	SDL_PauseAudio (0);

sleep(1024);
	// Wait for sound to complete 
	while (audio_len > 0) {
		SDL_Delay (100);         // Sleep 100 ms 
	}

	SDL_CloseAudio (); 
	return 0;
}
