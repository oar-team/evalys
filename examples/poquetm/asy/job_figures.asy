settings.outformat = "pdf";
unitsize(1cm);
from job access *;

Job generate_job()
{
    int s = 255, w=225;

    Job j;
    j.id = "$j$";
    j.submission_date = 0;
    j.processing_time = 3;
    j.requested_time = 4;
    j.number_of_requested_resources = 2;
    j.starting_time = 1;
    j.allocation_start = 0;
    j.fill_color = rgb(w,s,w);

    return j;
}

void figure_one_job_definition()
{
    // The job
    Job j = generate_job();

    draw_job(j, true);

    // The processing time
    real line_y = j.allocation_start - 0.25;
    draw((j.starting_time, line_y) --
         (j.starting_time + j.processing_time, line_y),
         black, Arrow);
    draw((j.starting_time, line_y) --
         (j.starting_time + j.processing_time, line_y) -- cycle,
         black, Arrow);
    label("$p_j$", (j.starting_time + j.processing_time/2.0, line_y), align=down);

    // The requested time
    real line_y = j.allocation_start + j.number_of_requested_resources + 0.5;
    draw((j.starting_time, line_y) --
         (j.starting_time + j.requested_time, line_y),
         black, Arrow);
    draw((j.starting_time, line_y) --
         (j.starting_time + j.requested_time, line_y) -- cycle,
         black, Arrow);
    label("$w_j$", (j.starting_time + j.requested_time/2.0, line_y), align=down);

    // The number of requested resources
    real line_x = j.starting_time - 0.25;
    draw((line_x, j.allocation_start) --
         (line_x, j.allocation_start + j.number_of_requested_resources),
         Arrow);
    draw((line_x, j.allocation_start) --
         (line_x, j.allocation_start + j.number_of_requested_resources) -- cycle,
         Arrow);
    label("$q_j$", (line_x, j.allocation_start + j.number_of_requested_resources/2.0),
          align=left);

    shipout("one_job");
}

void figure_one_job_more_attributes(bool draw_turnaround_time = true)
{
    // The job
    Job j = generate_job();
    j.id = "$j$";
    j.submission_date = 1;
    j.starting_time = 3;
    j.allocation_start = 1;

    draw_frame(0, 5, 0, 3, draw_time_axe_values=false,
               draw_machine_axe_values=false, draw_machine_axe_label=false,
               draw_machines_separations=false, draw_machines_axe = false);
    draw_job(j);

    // Release date bar
    real bars_y = 4;
    real times_y = -1/8;
    draw((j.submission_date,0) -- (j.submission_date,bars_y), black+linetype(new real[] {8,4}));
    label("$r_j$", (j.submission_date,times_y), align=down);

    // Starting date bar
    draw((j.starting_time,0) -- (j.starting_time,bars_y), black+linetype(new real[] {8,4}));
    label("$start_j$", (j.starting_time,times_y), align=down);

    // Completion date bar
    draw((j.starting_time + j.processing_time,0) -- (j.starting_time + j.processing_time,bars_y), black+linetype(new real[] {8,4}));
    label("$C_j$", (j.starting_time + j.processing_time,times_y), align=down);

    // Waiting time display
    real line_y = 3.25;
    draw((j.submission_date, line_y) -- (j.starting_time, line_y), Arrow);
    draw((j.submission_date, line_y) -- (j.starting_time, line_y) -- cycle, Arrow);
    label("$wait_j$", ((j.submission_date+j.starting_time)/2.0, line_y), align=up);

    // Turnaround time display
    if (draw_turnaround_time)
    {
        line_y = 4;
        draw((j.submission_date, line_y) -- (j.starting_time+j.processing_time, line_y), Arrow);
        draw((j.submission_date, line_y) -- (j.starting_time+j.processing_time, line_y) -- cycle, Arrow);
        label("$turnaround_j$", ((j.submission_date+j.starting_time+j.processing_time)/2.0, line_y), align=up);
    }

    shipout("one_job_context");
}

// Let's draw the figures.
figure_one_job_definition();
erase();

figure_one_job_more_attributes(draw_turnaround_time = false);
erase();
