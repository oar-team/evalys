settings.outformat = "pdf";
unitsize(1cm);
from job access *;

Job[] easy_bf_workload()
{
    int s = 255, w=225;
    Job j1 = Job("$1$", 0, 3, 4, 1, rgb(s,w,w));
    Job j2 = Job("$2$", 1, 2, 2, 2, rgb(w,w,s));
    Job j3 = Job("$3$", 2, 1, 1, 1, rgb(w,s,w));

    Job jobs[] = {j1, j2, j3};
    return jobs;
}

struct JobAlteration
{
    int requested_time;
    real starting_time;
    real allocation_start;
}

JobAlteration alt(int requested_time = 0,
                  real starting_time = 0,
                  real allocation_start = 0)
{
    JobAlteration a;
    a.requested_time = requested_time;
    a.starting_time = starting_time;
    a.allocation_start = allocation_start;

    return a;
}

Job apply_alt(Job job, JobAlteration alteration)
{
    Job j = job;
    j.requested_time += alteration.requested_time;
    j.starting_time += alteration.starting_time;
    j.allocation_start += alteration.allocation_start;

    return j;
}

void init_drawing(int time, real max_x = 0, real max_y = -5)
{
    erase();

    // Invisible dot to make sure all figures have the same size
    draw(circle((max_x, max_y), 0));

    // Draw the frame (time and machine axis)
    draw_frame(0, 7, 0, 2,
               current_time = time,
               draw_current_time = true);
}

void draw_current_time(int time, real time_y = 2)
{
    // vertical line
    draw((time, 0) -- (time, time_y), linewidth(2));

    // let's shade the past
    path past_rect = (0, 0) -- (time, 0) --
                     (time, time_y) -- (0, time_y) -- cycle;
    filldraw(past_rect, black + opacity(0.2), opacity(0));
}

void draw_current_state(Job jobs[],
                        bool display_jobs[],
                        int current_time)
{
    // Display previous jobs
    for (int i = 0; i < jobs.length; ++i)
        if (display_jobs[i])
            draw_job(jobs[i], true);

    // Display the current time
    draw_current_time(current_time);
}

void draw_easy_animation()
{
    Job easy_jobs[] = easy_bf_workload();
    int nb_jobs = 3;
    bool display_jobs[] = {false, false, false};

    int[][] release_times = {
        {},
        {0},
        {1},
        {2},
        {}, {}, {}
    };

    JobAlteration[][] alterations_to_do = {
        {alt(), alt(), alt()},
        {alt(0,1), alt(), alt()}, // j0 is launched now
        {alt(), alt(0,5), alt()}, // j1 is reserved after j0
        {alt(), alt(), alt(0,3,1)}, // j2 is launched now
        {alt(-1), alt(0,-1), alt()}, // j1 finishes before its walltime. j2 is launched now
        {alt(), alt(), alt()},
        {alt(), alt(), alt()}
    };

    string[] pre_text = {
        "", "", "", "", "Jobs $1$ and $3$ finished", "", ""
    };

    real released_now_x = 4;
    real released_now_y = -2.5;
    real time_y = 2;

    // For each time step
    for (int t = 0; t < 7; ++t)
    {
        if (length(pre_text[t]) > 0)
        {
            init_drawing(t);
            draw_current_state(easy_jobs, display_jobs, t);
            label(pre_text[t], (released_now_x, released_now_y), align=up);
            shipout("easy_bf" + string(t) + "_pre");
        }

        // Release new jobs
        int jobs_released_now[] = release_times[t];
        if (jobs_released_now.length > 0)
        {
            init_drawing(t);
            draw_current_state(easy_jobs, display_jobs, t);

            for (int i = 0; i < jobs_released_now.length; ++i)
            {
                int released_job = jobs_released_now[i];
                display_jobs[released_job] = true;
            }

            Job first_released_job = easy_jobs[jobs_released_now[0]];
            draw_job_on_position(first_released_job,
                                 (released_now_x, released_now_y),
                                 draw_requested_time=true,
                                 centered=true);
            label("New job!", (released_now_x, released_now_y+first_released_job.number_of_requested_resources/2), align=up);

            shipout("easy_bf" + string(t) + "_rel");
        }

        // Take alterations into account
        JobAlteration alterations_to_do_now[] = alterations_to_do[t];
        for (int i = 0; i < nb_jobs; ++i)
            easy_jobs[i] = apply_alt(easy_jobs[i], alterations_to_do_now[i]);

        init_drawing(t);
        draw_current_state(easy_jobs, display_jobs, t);

        // Generate the figure then clean the current drawing state
        shipout("easy_bf" + string(t));
    }
}


draw_easy_animation();
